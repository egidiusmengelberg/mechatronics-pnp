import cv2
import numpy as np
from math import tan, sin, cos, pi, atan2, sqrt

def drawAxis(img, p_, q_, color, scale):
  p = list(p_)
  q = list(q_)
 
  ## [visualization1]
  angle = atan2(p[1] - q[1], p[0] - q[0]) # angle in radians
  hypotenuse = sqrt((p[1] - q[1]) * (p[1] - q[1]) + (p[0] - q[0]) * (p[0] - q[0]))
 
  # Here we lengthen the arrow by a factor of scale
  q[0] = p[0] - scale * hypotenuse * cos(angle)
  q[1] = p[1] - scale * hypotenuse * sin(angle)
  cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, 3, cv2.LINE_AA)
 
  # create the arrow hooks
  p[0] = q[0] + 9 * cos(angle + pi / 4)
  p[1] = q[1] + 9 * sin(angle + pi / 4)
  cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, 3, cv2.LINE_AA)
 
  p[0] = q[0] + 9 * cos(angle - pi / 4)
  p[1] = q[1] + 9 * sin(angle - pi / 4)
  cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, 3, cv2.LINE_AA)
  ## [visualization1]
 
def getOrientation(pts, img):
  ## [pca]
  # Construct a buffer used by the pca analysis
  sz = len(pts)
  data_pts = np.empty((sz, 2), dtype=np.float64)
  for i in range(data_pts.shape[0]):
    data_pts[i,0] = pts[i,0,0]
    data_pts[i,1] = pts[i,0,1]
 
  # Perform PCA analysis
  mean = np.empty((0))
  mean, eigenvectors, eigenvalues = cv2.PCACompute2(data_pts, mean)
 
  # Store the center of the object
  cntr = (int(mean[0,0]), int(mean[0,1]))
  ## [pca]
 
  ## [visualization]
  # Draw the principal components
  cv2.circle(img, cntr, 3, (255, 0, 255), 2)
  p1 = (cntr[0] + 0.02 * eigenvectors[0,0] * eigenvalues[0,0], cntr[1] + 0.02 * eigenvectors[0,1] * eigenvalues[0,0])
  p2 = (cntr[0] - 0.02 * eigenvectors[1,0] * eigenvalues[1,0], cntr[1] - 0.02 * eigenvectors[1,1] * eigenvalues[1,0])
  drawAxis(img, cntr, p1, (255, 255, 0), 1)
  drawAxis(img, cntr, p2, (0, 0, 255), 5)
 
  angle = atan2(eigenvectors[0,1], eigenvectors[0,0]) # orientation in radians
  ## [visualization]
 
  # Label with the rotation angle
  label = "  Rotation Angle: " + str(-int(np.rad2deg(angle)) - 90) + " degrees"
  textbox = cv2.rectangle(img, (cntr[0], cntr[1]-25), (cntr[0] + 250, cntr[1] + 10), (255,255,255), -1)
  cv2.putText(img, label, (cntr[0], cntr[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
 
  return angle

def find_color(image, contour):
    M = cv2.moments(contour)
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    kleur = image[cy, cx]
    return kleur

def detect_shapes(img):
    threshold1 = cv2.getTrackbarPos('Threshold1', 's')
    threshold2 = cv2.getTrackbarPos('Threshold2', 's')

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)
    edges = cv2.Canny(imgBlur, threshold1, threshold2)

    hsv_frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    y, x = img.shape[:2]
    hsv_pixel = hsv_frame[y // 2, x // 2]
    h, s, v = hsv_pixel[0], hsv_pixel[1], hsv_pixel[2]

    blauw_bereik = (88, 138)
    groen_bereik = (40, 75)
    rood_bereik = [(0, 14), (165, 180)]  # Rood heeft een gespleten bereik vanwege kleurcirkel
    paars_bereik = (143, 156)
    geel_bereik = (32, 40)
    oranje_bereik = (14, 32)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:
            M = cv2.moments(contour)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            epsilon = 0.04 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            corners = len(approx)

            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            hoek = int(rect[2])
            center = (int(rect[0][0]), int(rect[0][1]))
            width = int(rect[1][0])
            height = int(rect[1][1])
            if width < height:
                hoek = 90 - hoek
            else:
                hoek = -hoek

            label = str(hoek) + "graden"

            dot_region = img[cy + img.shape[0] // 2 - 5: cy + img.shape[0] // 2 + 5,
                            cx + img.shape[1] // 2 - 5: cx + img.shape[1] // 2 + 5]

            mean_hue = 0  # Set a default value
            mean_saturation = 0  # Set a default value

            if dot_region.shape[0] > 0 and dot_region.shape[1] > 0:
                dot_region_hsv = cv2.cvtColor(dot_region, cv2.COLOR_BGR2HSV)
                if np.any(dot_region_hsv):
                    mean_hue = np.mean(dot_region_hsv[:, :, 0])
                    mean_saturation = np.mean(dot_region_hsv[:, :, 1])

                if corners == 4:
                    if area > 13350:
                        blokje = "geel"
                    else:
                        blokje = "paars"
                elif corners == 3:
                    color = find_color(img, contour)
                    if area < 10000:
                        if mean_hue < 150 and mean_saturation < 90:
                            blokje = "wit"
                        #    blokje = "blauw"
                        else:
                            blokje = "blauw"
                        #    blokje = "wit"
                    elif area > 20000:
                        #if mean_saturation > 15:
                        if mean_hue > 160 and mean_saturation > 100:
                            blokje = "groen"
                        else:
                            blokje = "oranje"
                    else:
                        blokje = "rood"
                else:
                    blokje = "niet herkenbaar"

                return blokje, cx, cy, hoek, mean_hue, mean_saturation, area

    return None, None, None, None, None, None, None


def empty(a):
    pass

cap = cv2.VideoCapture(0)
cv2.namedWindow('s')
cv2.createTrackbar('Threshold1', 's', 69, 255, empty)
cv2.createTrackbar('Threshold2', 's', 255, 255, empty)
cv2.namedWindow('Webcam with Manual Lighting')
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
cap.set(cv2.CAP_PROP_AUTO_WB, 0.0)
initial_focus = 160
cap.set(cv2.CAP_PROP_FOCUS, initial_focus)
initial_brightness = 41
initial_contrast = 40
initial_saturation = 59
cap.set(cv2.CAP_PROP_BRIGHTNESS, initial_brightness)
cap.set(cv2.CAP_PROP_CONTRAST, initial_contrast)
cap.set(cv2.CAP_PROP_SATURATION, initial_saturation)


def update_brightness(brightness):
    cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)

def update_contrast(contrast):
    cap.set(cv2.CAP_PROP_CONTRAST, contrast)

def update_saturation(saturation):
    cap.set(cv2.CAP_PROP_SATURATION, saturation)

cv2.createTrackbar('Brightness', 'Webcam with Manual Lighting', initial_brightness, 200, update_brightness)
cv2.createTrackbar('Contrast', 'Webcam with Manual Lighting', initial_contrast, 200, update_contrast)
cv2.createTrackbar('Saturation', 'Webcam with Manual Lighting', initial_saturation, 200, update_saturation)
cv2.createTrackbar('Focus', 'Webcam with Manual Lighting', initial_focus, 255, lambda x: cap.set(cv2.CAP_PROP_FOCUS, x))

while True:
    _, img = cap.read()

    if not _:
        break

    blokje, cx, cy, hoek, mean_hue, mean_saturation, area = detect_shapes(img)

    if blokje is not None:
        print(f"Blokje: {blokje}, cx: {cx}, cy: {cy}, hoek: {hoek}, mean_hue: {mean_hue}, mean_saturation: {mean_saturation}, area:{area}")

    cv2.imshow('s', img)
    
    if cv2.waitKey(10) == 27:
        break

cap.release()
cv2.destroyAllWindows()
