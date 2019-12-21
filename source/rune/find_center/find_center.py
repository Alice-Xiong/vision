# import the necessary packages
import numpy as np
import argparse
import imutils
import cv2

from source.module import Module
from source.rune.predict_target.assign_panels.assign_panels import AssignPanels



class FindCenter(Module):
    
    def __init__(self, parent, state=None):
        self.working_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(self.working_dir, state=state)
        

    def process(self, image):
        """[Finds the center of the Rune using template matching on the letter R]
        
        Arguments:
            image {[list]} -- [image as a 3d list (rgb) ]
        
        Returns:
            [list] -- [returns list of x,y centers for Rune center]
        """
        template = cv2.imread("assets/template.png")
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # Depending on whether we are doing edge template matching,
        # we will run edge filter on the template
        if self.properties.edge_matching == 1:
            template = cv2.Canny(template, 50, 200)
            
        (tH, tW) = template.shape[:2]
        cv2.imshow("Template", template)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  
        found = None

        # loop over the scales of the image
        for scale in np.linspace(self.properties.filters["smallest_scale"], self.properties.filters["largest_scale"], self.properties.filters["number_of_filters"])[::-1]:
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break

            # We will ues the properties method in the json settings
            method = eval(self.properties.methods[self.properties.method])

            # Depending on whether we are doing edge template matching,
            # we will run edge filter on the image
            if self.properties.edge_matching == 1:
                edged = cv2.Canny(resized, 50, 200)
                result = cv2.matchTemplate(edged, template, method)
            else:
                result = cv2.matchTemplate(resized, template, method)
            
            (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)


            # Depending on the value, we must switch between the 
            # max of min value for the template matching result
            # if we have found a new maximum or minimum correlation value,
            # then we update the bookkeeping variable
            if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
                if found is None or minVal < found[0]:
                    found = (minVal, minLoc, r)
            else:
                if found is None or maxVal > found[0]:
                    found = (maxVal, maxLoc, r)

            

        # unpack the bookkeeping variable and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio
        (_, bestLoc, r) = found
        (startX, startY) = (int(bestLoc[0] * r), int(bestLoc[1] * r))
        (endX, endY) = (int((bestLoc[0] + tW) * r), int((bestLoc[1] + tH) * r))

        # draw a bounding box around the detected result and display the image
        # if required
        if properties.draw = 1:
            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
            cv2.imshow("Image", image)
            cv2.waitKey(0)
        
        return [int((startX + endX) / 2), int((startY + endY) / 2)]

