def Smooth(x,beta,window_len=11):
    from numpy import r_, kaiser, convolve
    """ kaiser window smoothing """
    # extending the data at beginning and at the end
    # to apply the window at the borders
    s = r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    w = kaiser(window_len,beta)
    y = convolve(w/w.sum(),s,mode='valid')
    return y[(window_len-1)/2:len(y)-(window_len-1)/2]
    
