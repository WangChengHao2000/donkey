import cv2
import numpy as np
import math


def draw_line(frame):
    height, width, _ = frame.shape
    BGRframe = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(BGRframe, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([15, 40, 40])
    upper_blue = np.array([45, 255, 255])

    yellow_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    yellow_edge = cv2.Canny(yellow_mask, 200, 400)
    yellow_region = region_of_interest(yellow_edge)

    lines = detect_line(yellow_region)
    lane_lines = average_lines(yellow_region, lines)

    line_frame = display_line(frame, lane_lines)

    x_offset = 0
    y_offset = 0
    if lane_lines != None and len(lane_lines) > 0:
        _, _, x2, _ = lane_lines[0][0]
        mid = int(width / 2)
        x_offset = x2 - mid
        y_offset = int(height / 2)
    else:
        print("检测不到行道线")
        return [None, line_frame]

    angle_to_mid_radian = math.atan(x_offset / y_offset)
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)
    steering_angle = angle_to_mid_deg / 45.0

    return steering_angle, line_frame


def region_of_interest(edges):
    height, width = edges.shape
    mask = np.zeros_like(edges)

    polygon = np.array(
        [
            [
                (width / 4, height / 2),
                (width * 3 / 4, height / 2),
                (width * 3 / 4, height),
                (width / 4, height),
            ]
        ],
        np.int32,
    )

    cv2.fillPoly(mask, polygon, 255)

    croped_edge = cv2.bitwise_and(edges, mask)
    return croped_edge


def detect_line(edges):
    rho = 1
    angle = np.pi / 180
    min_thr = 10
    lines = cv2.HoughLinesP(
        edges, rho, angle, min_thr, np.array([]), minLineLength=8, maxLineGap=8
    )
    return lines


def average_lines(frame, lines):
    lane_lines = []
    if lines is None:
        return lane_lines
    fits = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            if x1 == x2:
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            fits.append((slope, intercept))
    if len(fits) > 0:
        fit_average = np.average(fits, axis=0)
        lane_lines.append(make_points(frame, fit_average))
    return lane_lines


def make_points(frame, line):
    height, width = frame.shape
    slope, intercept = line
    y1 = height
    y2 = int(y1 * 1 / 2)
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]


def display_line(frame, lines, line_color=(0, 0, 255), line_width=2):
    line_img = np.zeros_like(frame)
    print(lines)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_img, (x1, y1), (x2, y2), line_color, line_width)
    line_img = cv2.addWeighted(frame, 0.8, line_img, 1, 1)
    return line_img


if __name__ == "__main__":
    frame = cv2.imread("cv/line_img.jpg")
    # frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([90, 90, 90])
    upper_blue = np.array([120, 200, 200])
    yellow_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    cv2.imwrite("cv/yellow_11.jpg", yellow_mask)

    yellow_edge = cv2.Canny(yellow_mask, 200, 400)
    cv2.imwrite("cv/yellow_21.jpg", yellow_edge)

    yellow_region = region_of_interest(yellow_edge)
    cv2.imwrite("cv/yellow_31.jpg", yellow_region)

    lines = detect_line(yellow_region)
    lane_lines = average_lines(yellow_region, lines)

    line_img = display_line(frame, lane_lines)
    cv2.imwrite("cv/yellow_41.jpg", line_img)
