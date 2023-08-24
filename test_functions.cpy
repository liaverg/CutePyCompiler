def main_parent():
#{
    #$ Declarations #$
    #declare var_parent, var, var_result

    def child1():
    #{
        return (var_parent * var);
    #}

    def child2(flag):
    #{
        #declare temp

        def grandchild():
        #{
            return (var_parent * var);
        #}

        if(flag == 0):
            temp = child1();
        else:
            var = 2;
            temp = grandchild();
        return (temp);
    #}

    var_parent = 10;
    var = 1;
    var_result = child2(0);
    print(var_result);
    var_result = child2(1);
    print(var_result);
#}


if __name__ == "__main__":
    main_parent();


