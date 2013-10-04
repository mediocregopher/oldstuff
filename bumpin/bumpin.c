d(i) {
    putchar(
        i// | (i << 8) | (i << 16) | (i << 24)
    );
}

main(i){for(i=0;;i++)d(i);}

//for (i=0;;i++)
//    putchar(
//        //((i*(i>>8|i>>9)&46&i>>8))^(i&i>>13|i>>6)
//    );
