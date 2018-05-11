/**
 * @author See Contributors.txt for code contributors and overview of BadgerDB.
 *
 * @section LICENSE
 * Copyright (c) 2012 Database Group, Computer Sciences Department, University of Wisconsin-Madison.
 */

/*! Authors Fayi Zhang, Huawei Wang, Wolong Yuan. */
#include <memory>
#include <iostream>
#include "buffer.h"
#include "exceptions/buffer_exceeded_exception.h"
#include "exceptions/page_not_pinned_exception.h"
#include "exceptions/page_pinned_exception.h"
#include "exceptions/bad_buffer_exception.h"
#include "exceptions/hash_not_found_exception.h"

namespace badgerdb { 

/*! Authors: Fayi Zhang, Huawei Wang, Wolong Yuan. */
BufMgr::BufMgr(std::uint32_t bufs)
	: numBufs(bufs) {
	bufDescTable = new BufDesc[bufs];

  for (FrameId i = 0; i < bufs; i++) 
  {
  	bufDescTable[i].frameNo = i;
  	bufDescTable[i].valid = false;
  }

  bufPool = new Page[bufs];

	int htsize = ((((int) (bufs * 1.2))*2)/2)+1;
  hashTable = new BufHashTbl (htsize);  // allocate the buffer hash table

  clockHand = bufs - 1;
}


BufMgr::~BufMgr() {
  clockHand = 0;
  /*! Find the pages that are valid and dirty, write them to disk. */
  for (uint32_t i = 0; i < numBufs; i++) {
    if (bufDescTable[i].valid && bufDescTable[i].dirty) {
      bufDescTable[i].file->writePage(bufPool[bufDescTable[i].frameNo]);
    }
  }
  /*! Then delete all the tables that are allocated using in the constructor. */
  delete [] hashTable;
  delete [] bufPool;
  delete [] bufDescTable;
}

void BufMgr::advanceClock()
{
  /*! Advance the clockHand and make sure it is in the right range. */
  clockHand = (clockHand + 1) % numBufs;
}

void BufMgr::allocBuf(FrameId & frame) 
{
  
  uint32_t numPinned = 0;
  uint32_t start = clockHand;
  /*! Search in the buffer, if find one, then return, otherwise if after a round find all the buffers are pinned, throw exception about it. */
  while (numPinned < numBufs) {
    /*! After a round if numPinned is not full, reset to 0 to avoid confusion. */
    if (start == clockHand) {
      numPinned = 0;
    }
    BufDesc current = bufDescTable[clockHand];
    if (current.valid == false) {
      current.valid = true;
      advanceClock();
      frame = current.frameNo;
      return;
    }
    else if (current.refbit == true) {
      bufDescTable[clockHand].refbit = false;
    }
    else if (current.pinCnt > 0) {
      numPinned++;
    }
    else {
      if (current.dirty == true) {
        bufDescTable[clockHand].file->writePage(bufPool[current.frameNo]);
      }
      frame = current.frameNo;
      hashTable->remove(current.file, current.pageNo);
      bufDescTable[clockHand].Clear();
      advanceClock();
      return;
    }
    advanceClock();
  }
  /*! If out of the while loop because all are pinned, throw exception. */
  throw BufferExceededException();
}

	
void BufMgr::readPage(File* file, const PageId pageNo, Page*& page)
{
  /*! if in the buffer, return it, otherwise catch the exception, read it from the disk. */
  try {
    FrameId frame;
    hashTable->lookup(file, pageNo, frame);
    bufDescTable[frame].refbit = false;
    bufDescTable[frame].pinCnt++;
    page = &bufPool[frame];
  } catch (HashNotFoundException e) {
    Page pg = file->readPage(pageNo);
    FrameId frameId;
    allocBuf(frameId);
    bufPool[frameId] = pg;
    hashTable->insert(file, pageNo, frameId);
    page = &bufPool[frameId];
    bufDescTable[frameId].Set(file, pageNo);
  }
}


void BufMgr::unPinPage(File* file, const PageId pageNo, const bool dirty) 
{
  /*! if page not in the buffer, return. */
  FrameId frame;
  try {
    hashTable->lookup(file, pageNo, frame);
  } catch (HashNotFoundException e) {
    return;
  }
  /*! if pin count already 0, throw exception. */
  if (bufDescTable[frame].pinCnt == 0) {
    throw PageNotPinnedException(file->filename(), pageNo, frame);
    return;
  }
  /*! Decrease pin count, if zero, set the refbit to true. */
  bufDescTable[frame].pinCnt--;
  if (bufDescTable[frame].pinCnt == 0) {
    bufDescTable[frame].refbit = true;
  }
  if (dirty) {
    bufDescTable[frame].dirty = true;
  }
}

void BufMgr::flushFile(const File* file) 
{
  /*! Flush the buffer for a file, if pinned or not valid, throw exception. if dirty, write to disk */
  for (uint32_t i = 0; i < numBufs; i++) {
    BufDesc des = bufDescTable[i];
    if (des.file == file) {
      if (des.pinCnt > 0) {
        throw PagePinnedException(file->filename(), des.pageNo, des.frameNo);
      }
      if (!des.valid) {
        throw BadBufferException(des.frameNo, des.dirty, des.valid, des.refbit);
      }
      if (des.dirty) {
        des.file->writePage(bufPool[des.frameNo]);
        des.dirty = false;
      }
      /*! Then remove buffer. */
      hashTable->remove(file, des.pageNo);
      bufDescTable[i].Clear();
    }
  }
}

void BufMgr::allocPage(File* file, PageId &pageNo, Page*& page) 
{
  /*! Allocate a page for a file, allocate a frame in buffer for it and set it right in the buffer pool. */
  Page allo = file->allocatePage();
  FrameId frame;
  allocBuf(frame);
  hashTable->insert(file, allo.page_number(), frame);
  bufDescTable[frame].Set(file, allo.page_number());
  pageNo = allo.page_number();
  bufPool[frame] = allo;
  page = &bufPool[frame];
}

void BufMgr::disposePage(File* file, const PageId PageNo)
{
  /*! Delete a page in a file, if not in buffer, delete it directly, otherwise remove it from the buffer and then delete if from disk. */
  FrameId frame;
  try {
    hashTable->lookup(file, PageNo, frame);
  } catch (HashNotFoundException e) {
    file->deletePage(PageNo);
    return;
  }
  hashTable->remove(file, PageNo);
  bufDescTable[frame].Clear();
  file->deletePage(PageNo);
}

void BufMgr::printSelf(void) 
{
  BufDesc* tmpbuf;
	int validFrames = 0;
  
  for (std::uint32_t i = 0; i < numBufs; i++)
	{
  	tmpbuf = &(bufDescTable[i]);
		std::cout << "FrameNo:" << i << " ";
		tmpbuf->Print();

  	if (tmpbuf->valid == true)
    	validFrames++;
  }

	std::cout << "Total Number of Valid Frames:" << validFrames << "\n";
}

}
