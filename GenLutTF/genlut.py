import numpy as np
import pandas as pd
import tensorflow as tf


def predict(hr, hg, hb):
    tf_in = tf.convert_to_tensor([[hr, hg, hb]])
    sdr_out = model.predict(tf_in)
    sr, sg, sb = sdr_out[0]
    sr = np.clip(sr, 0.0, 255.0)
    sg = np.clip(sg, 0.0, 255.0)
    sb = np.clip(sb, 0.0, 255.0)
    return sr, sg, sb

def batch_predict(lst):
    tf_in = tf.convert_to_tensor(lst)
    return batch_predict_tf(tf_in)

def batch_predict_tf(tf_in):
    sdr_out = model.predict(tf_in)
    return np.clip(sdr_out, 0.0, 255.0)


def luti_to_hdr(i):
    step_size = 65535.0 / 65.0
    return step_size * i

def sdr_to_lutv(c):
    return c / 255.0

def write_lut():
    lut_file = open("../generated_lut.cube", "w+")
    lut_file.write("TITLE \"HDR_2_SDR_generated_lut\"")
    lut_file.write("\n")
    lut_file.write("LUT_3D_SIZE 65")
    lut_file.write("\n")
    for bi in range(0, 65):
        for gi in range(0, 65):
            for ri in range(0, 65):
                hr, hg, hb = luti_to_hdr(ri), luti_to_hdr(gi), luti_to_hdr(bi)
                sr, sg, sb = predict(hr, hg, hb)
                lr, lg, lb = sdr_to_lutv(sr), sdr_to_lutv(sg), sdr_to_lutv(sb)
                lut_file.write(f"{lr:.6f} {lg:.6f} {lb:.6f}")
                lut_file.write("\n")
    lut_file.close()


def write_lut_fast():
    lut_file = open("../generated_lut.cube", "w+")
    lut_file.write("TITLE \"HDR_2_SDR_generated_lut\"")
    lut_file.write("\n")
    lut_file.write("LUT_3D_SIZE 65")
    lut_file.write("\n")
    for bi in range(0, 65):
        for gi in range(0, 65):
            ril = list(range(0, 65))
            hdr_list = [[luti_to_hdr(ri), luti_to_hdr(gi), luti_to_hdr(bi)] for ri in ril]
            prediction_list = batch_predict(hdr_list)
            for sr, sg, sb in prediction_list:
                lr, lg, lb = sdr_to_lutv(sr), sdr_to_lutv(sg), sdr_to_lutv(sb)
                lut_file.write(f"{lr:.6f} {lg:.6f} {lb:.6f}")
                lut_file.write("\n")
    lut_file.close()


if __name__ == '__main__':
    pass
