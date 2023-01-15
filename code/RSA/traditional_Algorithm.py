
def decompose(num):
    n = num
    m=[]
    while n!=1:    #n==1时，已分解到最后一个质因数
        for i in range(2,n+1):
            if n % i == 0:
                m.append(str(i))    #将i转化为字符串再追加到列表中，便于使用join函数进行输出
                n = (int)(n/i)
        if n==1:
            break    #n==1时，循环停止
    
    print(num,'=','x'.join(m))

decompose(21)
