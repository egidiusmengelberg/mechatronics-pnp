import cv2
import numpy as np

def empty(a):
    pass

# middel punt zoeker
def find_color(image, contour):
    M = cv2.moments(contour)
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    kleur = image[cy, cx]
    return kleur

cap = cv2.VideoCapture(0)  
cv2.namedWindow('s')
cv2.resizeWindow('s', 600, 800)
cv2.createTrackbar('Threshold1', 's', 0, 255, empty)
cv2.createTrackbar('Threshold2', 's', 255, 255, empty)

while True:
    _, img = cap.read() 

    threshold1 = cv2.getTrackbarPos('Threshold1', 's')
    threshold2 = cv2.getTrackbarPos('Threshold2', 's')    
    
    imgBlur = cv2.GaussianBlur(img, (7, 7), 1)
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(imgGray, threshold1, threshold2)
    # vind de contours
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    yellow_lower = np.array([100, 100, 100], dtype=np.uint8)
    yellow_upper = np.array([255, 255, 255], dtype=np.uint8)
    blauw_lower = np.array([100, 100, 100], dtype=np.uint8)  
    blauw_upper = np.array([130, 255, 255], dtype=np.uint8)
    groen_lower = np.array([40, 100, 100], dtype=np.uint8)
    groen_upper = np.array([80, 255, 255], dtype=np.uint8)

    # voor elke contour
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:
            # Calculate number of corners
            epsilon = 0.04 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            corners = len(approx)

            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)

            hoek = int(rect[2])
            center = (int(rect[0][0]),int(rect[0][1])) 
            width = int(rect[1][0])
            height = int(rect[1][1])
            if width < height:
                    hoek = 90 - hoek
            else:
                    hoek = -hoek

            label = str(hoek) + "graden"

            # kijken welk blokje het is
            if corners == 4:
                mask = cv2.inRange(img, yellow_lower, yellow_upper)
                yellow_pixels = cv2.countNonZero(mask)
                if yellow_pixels > 0:  
                    kleur = "geel"
                else:
                    kleur = "paars"
            elif corners == 3:
                if area < 4000:
                    witzoek = cv2.inRange(img, blauw_lower, blauw_upper)
                    witaantal = cv2.countNonZero(witzoek)
                    if witaantal < 1000: 
                        kleur = "wit"
                    else:
                        kleur = "blauw"
                elif area > 10000:
                    groenzoek = cv2.inRange(img, groen_lower ,groen_upper)
                    groenaantal = cv2.countNonZero(groenzoek)
                    if groenaantal < 100: 
                        kleur = "groen"
                    else:
                        kleur = "oranje"
                else:
                    kleur = "rood"

            # middelpunt zoeken
            M = cv2.moments(contour)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.circle(img, (cx, cy), 5, (255, 0, 0), -1)
            cv2.putText(img, f"Position: ({cx}, {cy})", (cx - 50, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 192, 203), 2)

            # teken contour over de shapes
            cv2.drawContours(img, [contour], -1, (0, 255, 0), 2)

            # laat informatie op scherm zien
            cv2.putText(img, f"Color: {kleur}", (cx - 50, cy + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 192, 203),
                        2)
            cv2.putText(img, f"Area: {area}", (cx - 50, cy + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 192, 203),
                        2)
            cv2.putText(img, label , (cx - 50, cy - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 2)


    cv2.imshow('s', img)
    cv2.imshow('saa', edges)

    if(cv2.waitKey(10) == 27):
        break

cap.release()
cv2.destroyAllWindows()
