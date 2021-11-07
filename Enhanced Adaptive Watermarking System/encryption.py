from pathlib import Path
import qrcode
from time import time
import cv2


class Encryption():
    def __init__(self) -> None:
        self.default_path = "output"
        self.qr_width = 37
        self.qr_height = 37

    def generate_folder(self, path) -> None:
        path = Path(path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

    def generate_qr_code(self, text) -> None:
        qr = qrcode.QRCode(
            version=1, box_size=1, border=4, error_correction=qrcode.constants.ERROR_CORRECT_Q)
        user_id_folder = text.split('_')[1]
        base_path = self.default_path + '/' + user_id_folder
        image_path = base_path + '/qr/' + str(int(time())) + '.png'
        self.generate_folder(base_path + '/qr')
        qr.add_data(image_path)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        self.qr_width, self.qr_height = img.size
        print(img.size)
        img.save(image_path)
        return image_path

    def embedded_qrcode(self, image_array, text):
        qr_row = 0
        qr_col = 0
        image_array = self.convert_image(image_array)
        is_already_available = self.check_if_available(image_array)
        if not is_already_available:
            path = self.generate_qr_code(text)
            qr_array = self.convert_image(cv2.imread(path), True)
            for rdx, row in enumerate(image_array):
                if rdx % self.qr_height == 0:
                    qr_row = 0
                for cdx, col in enumerate(row):
                    if cdx % self.qr_width == 0:
                        qr_col = 0
                    if col % 2 == 0 and qr_array[qr_row][qr_col] == 1:
                        image_array[rdx][cdx] = image_array[rdx][cdx] + 1
                    elif col % 2 == 1 and qr_array[qr_row][qr_col] == 0:
                        image_array[rdx][cdx] = image_array[rdx][cdx] - 1
                    qr_col = qr_col + 1
                qr_row = qr_row + 1
            path = path.replace("/qr", "/encoded").split("/")
            name = path.pop()
            path = "/".join(path)
            self.generate_folder(path)
            cv2.imwrite(path + '/' + name, image_array)
            self.save_qr_encodings(path + '/qr_encoding_' + name, image_array)
            return image_array
        return image_array

    def save_qr_encodings(self, path, image_array):
        image_array = (image_array % 2) * 255
        image_array2 = image_array[0:self.qr_height, 0:self.qr_width]
        path2 = path.replace("qr_encoding_", "qr_encoding_og")
        cv2.imwrite(path, image_array)
        cv2.imwrite(path2, image_array2)

    def check_if_available(self, image_array):
        image_array = (image_array % 2) * 255
        image_array2 = image_array[0:self.qr_height, 0:self.qr_width]
        cv2.imwrite("temp.jpg", image_array2)
        # if output:
        #     return True
        # return False
        return False

    def convert_image(self, img, is_qr_image=False):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if is_qr_image:
            (thresh, img) = cv2.threshold(img, 128,
                                          255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            return img // 255
        return img


enc = Encryption()
img = cv2.imread("output/123/encoded/1636287944.png")
enc.embedded_qrcode(img, 'hi_123')
