#!/usr/bin/env python3

from threading import Thread, Condition
import cv2
import os

# globals
outputDir    = 'frames'
clipFileName = 'clip.mp4'
# initialize frame count
count = 0


#will be available for all threads
queue1 = []

# need two queues
queue2 = []

#maximum size of queue, variable allows for quick changes
MAX_NUM = 10

condition1 = Condition() #prod to consumer one
condition2 = Condition() #consumerone to consumer twp


#producer thread really the first thread
#would be nice if lists where pass by reference
class Producer(Thread):
    def run(self):
        global queue1
        outputDir = 'frames'
        clipFileName = 'clip.mp4'
        # initialize frame count
        count = 0
        # open the video clip
        vidcap = cv2.VideoCapture(clipFileName)
        # create the output directory if it doesn't exist
        if not os.path.exists(outputDir):
            print("Output directory {} didn't exist, creating".format(outputDir))
            os.makedirs(outputDir)

        # read one frame
        success, image = vidcap.read()
        print("Reading frame {} {} ".format(count, success))
        while success:
            condition1.acquire()
            if len(queue1) == MAX_NUM:
                print ("Queue1 full, producer waiting")
                condition1.wait()
                print ("Space in queue1 now")
            # write the current frame out as a jpeg image
            #inFileName = cv2.imwrite("{}/frame_{:04d}.jpg".format(outputDir, count), image)
            queue1.append(image)
            #print ("Produced frame " + count)
            condition1.notify()
            condition1.release()
            success, image = vidcap.read()
            print('Reading frame {}'.format(count))
            count += 1
        print("Producer Done")

#consumer one is essentially
class ConsumerOne(Thread):
    def run(self):
        global queue1
        global queue2
        count = 0
        inputFrame = 1
        while inputFrame is not None:
            condition1.acquire()
            if not queue1:
                print ("Queue1 empty, waiting.....")
                condition1.wait()
                print ("Consumer1 has been notified of something pending")
            inputFrame = queue1.pop(0) #zero is necessary else the last index is popped
            #extra work needs to be done here
            grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)
            condition2.acquire()
            queue2.append(grayscaleFrame)
            if len(queue2) == MAX_NUM:
                print ("Queue2 full, producer waiting")
                condition2.wait()
                print ("Space in queue2 now")
                # need to do something here
            print('Reading frame {}'.format(count))
            count += 1
            condition2.notify()
            condition2.release()

class ConsumerTwo(Thread):
    def run(self):
        global queue2
        inputFrame = 1
        while inputFrame is not None:
            condition2.acquire()
            if not queue2:
                print ("Queue2 empty, waiting.....")
                condition2.wait()
                print ("Consumer2 has been notified of something pending")
            inputFrame = queue2.pop(0) #zero is necessary else the last index is popped
            print ("Consumer2 consumed something")
            cv2.imshow("Video", inputFrame)
            if cv2.waitKey(42) and 0xFF == ord("q"):
                break
        print("Finished")
        cv2.destroyAllWindows
        #extra work needs to be done here



Producer().start()
print("Running Producer")
ConsumerOne().start()
print("Running Consumer1")
ConsumerTwo().start()
print("Running Consumer2")