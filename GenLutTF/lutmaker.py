import numpy as np
import tensorflow as tf


def predict(model, hr, hg, hb):
    tf_in = tf.convert_to_tensor([[hr, hg, hb]])
    sdr_out = model.predict(tf_in)
    sr, sg, sb = sdr_out[0]
    sr = np.clip(sr, 0.0, 255.0)
    sg = np.clip(sg, 0.0, 255.0)
    sb = np.clip(sb, 0.0, 255.0)
    return sr, sg, sb


def batch_predict(model, lst):
    tf_in = tf.convert_to_tensor(lst)
    return batch_predict_tf(model, tf_in)


def batch_predict_tf(model, tf_in):
    sdr_out = model.predict(tf_in)
    return np.clip(sdr_out, 0.0, 255.0)


def luti_to_hdr(i, lut_size):
    lut_step_size = 65535.0 / lut_size
    return lut_step_size * i


def sdr_to_lutv(c):
    return c / 255.0


def write_lut_fast(filepath: str, model, lut_size: int) -> None:
    """
    Writes out the .cube file
    :param filepath: the .cube file path to write
    :param model: the tensorflow model for predicting
    :param lut_size: the size of the lut, usually 17, 33, 65. 129 has better quality but isn't always supported
    :return: None
    """
    lut_file = open(filepath, "w+")
    lut_file.write("TITLE \"HDR_2_SDR_generated_lut\"")
    lut_file.write("\n")
    lut_file.write("LUT_3D_SIZE " + str(lut_size))
    lut_file.write("\n")
    for bi in range(0, lut_size):
        for gi in range(0, lut_size):
            ril = list(range(0, lut_size))
            hdr_list = [[luti_to_hdr(ri, lut_size), luti_to_hdr(gi, lut_size), luti_to_hdr(bi, lut_size)] for ri in ril]
            prediction_list = batch_predict(model, hdr_list)
            for sr, sg, sb in prediction_list:
                lr, lg, lb = sdr_to_lutv(sr), sdr_to_lutv(sg), sdr_to_lutv(sb)
                lut_file.write(f"{lr:.6f} {lg:.6f} {lb:.6f}")
                lut_file.write("\n")
    lut_file.close()
