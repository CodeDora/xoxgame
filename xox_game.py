import cv2
import numpy as np
import random
import time 

cap = cv2.VideoCapture(0)

# Oyun tahtası boyutları
board_size = 450
cell_size = board_size // 3

# Renkler için bu kısımdan değişiklikler yapabilirsin
white = (255, 255, 255)
line_color = (0, 0, 0)
x_color = (255, 0, 0)
o_color = (0, 0, 255)

# Oyun tahtası
board = [[""] * 3 for _ in range(3)]

# İşaret tanıma sınırları
FIST_THRESH = 150
OPEN_THRESH = 70

# İşaret tanıma fonksiyonu
def detect_gesture(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, FIST_THRESH, 255, cv2.THRESH_BINARY)
    
    # İşlemi iyileştirmek için dilate ve erode işlemleri uyguluyoruz
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(thresholded, kernel, iterations=2)
    eroded = cv2.erode(dilated, kernel, iterations=1)
    
    contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(max_contour)
        
        if area > OPEN_THRESH:
            return "OPEN"
        else:
            return "FIST"
    else:
        return None

# Sıradaki oyuncuyu belirleme
current_player = "player"  # Başlangıçta oyuncu başlar

# Seçili sembol
player_symbol = "X"
computer_symbol = "O"

def toggle_player():
    global current_player
    if current_player == "player":
        current_player = "computer"
    else:
        current_player = "player"

def check_winner(symbol):
    for row in range(3):
        if all(board[row][col] == symbol for col in range(3)):
            return True
    for col in range(3):
        if all(board[row][col] == symbol for row in range(3)):
            return True
    if all(board[i][i] == symbol for i in range(3)):
        return True
    if all(board[i][2 - i] == symbol for i in range(3)):
        return True
    return False

def is_board_full():
    return all(all(cell != "" for cell in row) for row in board)

def reset_board():
    global board
    board = [[""] * 3 for _ in range(3)]

def draw_winner(frame, winner):
    winner_text = f"{winner} kazandi!"
    text_size = cv2.getTextSize(winner_text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
    text_x = (frame.shape[1] - text_size[0]) // 2
    text_y = (frame.shape[0] + text_size[1]) // 2
    cv2.putText(frame, winner_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2, line_color, 3, cv2.LINE_AA)

while True:
    ret, frame = cap.read()
    
    # İşaret tanıma noktası burdan başlıyor
    gesture = detect_gesture(frame)
    
    if current_player == "player":
        if gesture == "OPEN":
            # İşaret parmağının konumunu tespit ederek sembol yerleştirme işlemini gerçekleştirme
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv_frame, np.array([0, 120, 70]), np.array([20, 255, 255]))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                max_contour = max(contours, key=cv2.contourArea)
                (x, y), _ = cv2.minEnclosingCircle(max_contour)
                prev_x, prev_y = int(x), int(y)
                
                row = prev_y // cell_size
                col = prev_x // cell_size
                
                if 0 <= row < 3 and 0 <= col < 3 and board[row][col] == "":
                    board[row][col] = player_symbol
                    if check_winner(player_symbol):
                        draw_winner(frame, "Oyuncu")
                        cv2.imshow("XOX Oyunu", frame)
                        cv2.waitKey(5000)  
                        reset_board()
                        toggle_player()
                    elif is_board_full():
                        draw_winner(frame, "Berabere")
                        cv2.imshow("XOX Oyunu", frame)
                        cv2.waitKey(5000)  # 5 saniye beklet
                        reset_board()
                        toggle_player()
                    else:
                        toggle_player()
    elif current_player == "computer":
        empty_cells = [(row, col) for row in range(3) for col in range(3) if board[row][col] == ""]
        if empty_cells:
            row, col = random.choice(empty_cells)
            board[row][col] = computer_symbol
            if check_winner(computer_symbol):
                draw_winner(frame, "Bilgisayar")
                cv2.imshow("XOX Oyunu", frame)
                cv2.waitKey(5000)  # 5 saniye beklet
                reset_board()
                toggle_player()
            elif is_board_full():
                draw_winner(frame, "Berabere")
                cv2.imshow("XOX Oyunu", frame)
                cv2.waitKey(5000)  # 5 saniye beklet
                reset_board()
                toggle_player()
            else:
                toggle_player()

    # Oyun tahtası çizimi için gerekli kısım
    for i in range(1, 3):
        cv2.line(frame, (i * cell_size, 0), (i * cell_size, board_size), line_color, 2)
        cv2.line(frame, (0, i * cell_size), (board_size, i * cell_size), line_color, 2)
    
    # Oyun tahtasındaki sembolleri çizme işlemi yapıyor
    for row in range(3):
        for col in range(3):
            if board[row][col] == "X":
                cv2.putText(frame, "X", (col * cell_size + 30, row * cell_size + 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 3, x_color, 3, cv2.LINE_AA)
            elif board[row][col] == "O":
                cv2.putText(frame, "O", (col * cell_size + 30, row * cell_size + 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 3, o_color, 3, cv2.LINE_AA)
    
    cv2.imshow("XOX Oyunu", frame)

    # Çıkış için "q" tuşuna basılıp basılmadığını kontrol ediyoruz
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kapatma işlemi yapıyor
cap.release()
cv2.destroyAllWindows()


# buraya kadar geldiğine sevindim umarım daha iyilerini geliştiririm ve daha stabil çalışır hale getirebilirim <3
