import cv2
import numpy as np
import math


def draw_line(frame, record = False):
    height, width, _ = frame.shape
    BGRframe = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(BGRframe, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([0, 0, 0])
    upper_blue = np.array([180, 255, 46])
    yellow_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    lower_blue = np.array([0, 0, 0])
    upper_blue = np.array([180, 255, 46])
    white_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    yellow_edge = cv2.Canny(yellow_mask, 200, 400)
    white_edge = cv2.Canny(white_mask, 200, 400)

    yellow_roi = region_of_interest(yellow_edge, color="yellow")
    white_roi = region_of_interest(white_edge, color="white")

    yellow_lines = detect_line(yellow_roi)
    yellow_lane = average_lines(frame, yellow_lines, direction="left")
    white_lines = detect_line(white_roi)
    white_lane = average_lines(frame, white_lines, direction="right")

    line_frame = display_two_line(frame, yellow_lane, white_lane)
    
    if record:
        cv2.imwrite("cv/result.jpg", line_frame)

    x_offset = 0
    y_offset = 0
    if len(yellow_lane) > 0 and len(white_lane) > 0:
        _, _, left_x2, _ = yellow_lane[0][0]
        _, _, right_x2, _ = white_lane[0][0]
        mid = int(width / 2)
        x_offset = (left_x2 + right_x2) / 2 - mid
        y_offset = int(height / 2)
    elif len(yellow_lane) > 0 and len(yellow_lane[0]) == 1:
        x1, _, x2, _ = yellow_lane[0][0]
        x_offset = x2 - x1
        y_offset = int(height / 2)
    elif len(white_lane) > 0 and len(white_lane[0]) == 1:
        x1, _, x2, _ = white_lane[0][0]
        x_offset = x2 - x1
        y_offset = int(height / 2)
    else:
        print("检测不到行道线")
        return None, line_frame

    angle_to_mid_radian = math.atan(x_offset / y_offset)
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)
    steering_angle = angle_to_mid_deg / 45.0

    return steering_angle, line_frame


def region_of_interest(edges, color="yellow"):
    height, width = edges.shape
    mask = np.zeros_like(edges)
    if color == "yellow":
        polygon = np.array(
            [
                [
                    (0, height * 1 / 2),
                    (width * 1 / 2, height * 1 / 2),
                    (width * 1 / 2, height),
                    (0, height),
                ]
            ],
            np.int32,
        )
    else:
        polygon = np.array(
            [
                [
                    (width * 1 / 2, height * 1 / 2),
                    (width, height * 1 / 2),
                    (width, height),
                    (width * 1 / 2, height),
                ]
            ],
            np.int32,
        )
    cv2.fillPoly(mask, polygon, 255)
    croped_edge = cv2.bitwise_and(edges, mask)
    return croped_edge


def detect_line(edges):
    rho = 1  # 距离精度：1像素
    angle = np.pi / 180  # 角度精度：1度
    min_thr = 10  # 最少投票数
    lines = cv2.HoughLinesP(
        edges, rho, angle, min_thr, np.array([]), minLineLength=8, maxLineGap=8
    )
    return lines


def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height
    y2 = int(y1 * 1 / 2)
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]


def average_lines(frame, lines, direction="left"):
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
            if direction == "left" and slope < 0:
                fits.append((slope, intercept))
            elif direction == "right" and slope > 0:
                fits.append((slope, intercept))
    if len(fits) > 0:
        fit_average = np.average(fits, axis=0)
        lane_lines.append(make_points(frame, fit_average))
    return lane_lines


def display_line(frame, lines, line_color=(0, 0, 255), line_width=2):
    line_img = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_img, (x1, y1), (x2, y2), line_color, line_width)
    line_img = cv2.addWeighted(frame, 0.8, line_img, 1, 1)
    return line_img


def display_two_line(frame, yellow_lines, white_lines, line_width=2):
    line_img = np.zeros_like(frame)
    if yellow_lines is not None:
        for line in yellow_lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_img, (x1, y1), (x2, y2), (0, 255, 0), line_width)
    if white_lines is not None:
        for line in white_lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_img, (x1, y1), (x2, y2), (0, 0, 255), line_width)
    line_img = cv2.addWeighted(frame, 0.8, line_img, 1, 1)
    return line_img


if __name__ == "__main__":
    frame = cv2.imread("cv/test.jpg")
    draw_line(frame=frame, record=True)
