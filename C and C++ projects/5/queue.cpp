#include <stdlib.h>
#include <stdio.h>
#define MAXLENGTH 10
typedef int DataType;

typedef struct Queue
{
	int front, rear;  //индексы головы и хвоста
	DataType data[MAXLENGTH]; //массив для хранения элементов
} Queue;

void MakeNull (Queue *pqueue);
int Empty (Queue *pqueue);  //проверка на пустоту
int Full (Queue *pqueue);  //проверка на полноту заполнения
DataType Front (Queue *pqueue);  //неразрушающее чтение элемента
int EnQueue (DataType x, Queue *pqueue);  //добавление элемента в очередь
DataType DeQueue (Queue *pqueue);   //извлечение элемента из очереди

int main()
{
	Queue queue;
	int i;
	MakeNull(&queue);
	for (i=1; i<6; i++)
		EnQueue (i, &queue);
    while (!Empty(&queue))
		printf("%d ",DeQueue (&queue));
	system("pause");
	return 0;
}

void MakeNull (Queue *pqueue)
{
	pqueue->front = 0;
	pqueue->rear = MAXLENGTH-1;
}

int Empty(Queue *pqueue)
{
	return (pqueue->rear+1)%MAXLENGTH == pqueue->front;
}

int Full(Queue *pqueue)
{
	return (pqueue->rear+2)%MAXLENGTH == pqueue->front;
}

int Front (Queue *pqueue)
{
	return pqueue->data[pqueue->front];
}

int EnQueue (DataType x, Queue *pqueue)
{
	if (Full(pqueue)) return 0;
	pqueue->rear = (pqueue->rear+1)%MAXLENGTH;
    pqueue->data[pqueue->rear] = x;
    return 1;
}

DataType DeQueue (Queue *pqueue)
{
	int temp = pqueue->front;
    pqueue->front = (pqueue->front+1)%MAXLENGTH;
    return pqueue->data[temp];
}
