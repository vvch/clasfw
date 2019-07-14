def complex_format(c, real_f="{:f}", imag_f=None):
    if c is not None:
        if imag_f is not None:
            c = (real_f + ' ' + imag_f).format(c.real, c.imag)
        else:
            c = real_f.format(c)
    return "{}".format(c)