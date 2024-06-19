   //Поиск в глубину рекурсивный

#include <conio.h>
#include <iostream>
#define N 10

using namespace std;

FILE *fp = fopen("9.txt", "w");

    int G[N][N]={0,1,0,0,1,1,1,0,0,0,
                 1,0,1,1,1,1,1,0,0,1,
                 0,1,0,1,0,1,0,0,1,0,
                 0,1,1,0,1,1,0,1,0,0,
                 1,1,0,1,0,1,1,1,1,1,
                 1,1,1,1,1,0,0,1,1,1,
                 1,1,0,0,1,0,0,1,0,0,
                 0,0,0,1,1,1,1,0,1,0,           // исходный граф
                 0,0,1,0,1,1,0,1,0,1,
                 0,1,0,0,1,1,0,0,1,0},

    P[N]={0,0,0,0,0,0}, c=0;

int next (int i, int cur)
{
    cur++;
    while (cur<N && !G[i][cur]) cur++;
    if (cur<N) return cur;
    return -1;
}

void DFSR (int x)
{
	int y;

	P[x] = ++c; //помещаем вершину в путь
	y = next (x, -1);
    while (y != -1)  //пока есть смежные вершины
	{
        if (!P[y])   //если вершины еще нет в пути
            DFSR (y);       //продолжаем с нее обход
        y = next (x, y); //переходим к следующей вершине
    }
}

main()
{
    int x;

	DFSR(1);
    for (x=0; x<N; x++)
        {
            printf("%3d",P[x]);
            fprintf(fp,"%3d",P[x] );
        }
    getch();
    return 0;
}
