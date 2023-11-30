import cv2
import numpy as np

# Functie om middelpunt te zoeken
def middelpunt(contour):
    M = cv2.moments(contour)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return cX, cY
    else:
        return None

# Kleurwaardes definieren
colors = {
    'rood': ([0, 100, 100], [10, 255, 255]),
    'blauw': ([100, 100, 100], [130, 255, 255]),
    'groen': ([40, 100, 100], [80, 255, 255]),
    'paars': ([130, 100, 100], [170, 255, 255]),
    'oranje': ([10, 100, 100], [25, 255, 255]),
    'wit': ([0, 0, 200], [180, 50, 255])
}

# webcam kiezen
cap = cv2.VideoCapture(0)

while True:
    _, img = cap.read()
    if not _:
        break

    # HSV waarde berekenen
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    for color_name, (laag, hoog) in colors.items():
        laag = np.array(laag, dtype=np.uint8)
        hoog = np.array(hoog, dtype=np.uint8)

        # Zoek naar kleur gespecificeerde
        mask = cv2.inRange(hsv, laag, hoog)

        # Vind de contour in de mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # proces elke contour
        for contour in contours:
            area = cv2.contourArea(contour)
            cv2.imshow("b", mask)
            if area > 100:  # filter kleine storingen 
                # Zoek het middelpunt
                midden = middelpunt(contour)
                if midden is not None:
                    cX, cY = midden

                    # teken een cirkel op het middelpunt
                    cv2.circle(img, (cX, cY), 7, (255, 255, 255), -1)
                    cv2.putText(img, color_name, (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    cv2.imshow('Beeld1', img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
