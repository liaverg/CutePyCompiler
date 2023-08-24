def main_func1():
#{
    #$ Declarations #$
    #declare var1, var2, temp

    var1 = int(input());
    var2 = 2;
    temp = var1 + var2;
    print(temp);
#}

def main_func2():
#{
    #declare var1, var2
    #declare temp

    var1 = 6;
    var2 = 10;

    while(var1 <= var2):
        var1 = 2 * var1;

    if(var1 != var2):
        print(var1);
    else:
    #{
        temp = var1 + var2;
        print(temp);
    #}
#}

if __name__ == "__main__":
    main_func1();
    main_func2();


