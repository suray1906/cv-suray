/*��������� ������ - ����, ��������� �������� - ������*/

#include <stdio.h>
#include <stdlib.h>
#define MAXLENGTH 10
#define DataType int
#define STACK struct Stack

struct Stack
{
int top;
DataType elements[MAXLENGTH];
};

void MakeNull (STACK *pstack);	/*������ ����*/
int Empty (STACK *pstack);		/*���� ����*/
int Full (STACK *pstack);       /*���� �����*/
DataType Top (STACK *pstack);		/*������� � �������*/
DataType Pop (STACK *pstack);		/*�������� ��������*/
int Push (DataType x, STACK *pstack);	    /*���������� ��������*/

int main()
{
STACK stack;
int i;
MakeNull(&stack);
for (i=1; i<6; i++)
	Push (i, &stack);
while (!Empty(&stack))
	printf("%d ", Pop(&stack));
system("pause");
return 0;
}

void MakeNull (STACK *pstack)
{
pstack->top = -1;
}

int Empty(STACK *pstack)
{
if (pstack->top < 0)
	return 1;
else
	return 0;
}

int Full (STACK *pstack)
{
 if (pstack->top==MAXLENGTH-1)
    return 1;
 else
    return 0;
}

DataType Top (STACK *pstack)
{
 return pstack->elements[pstack->top];
}

DataType Pop (STACK *pstack)
{
 pstack->top--;
 return pstack->elements[pstack->top+1];
}

int Push (int x, STACK *pstack)
{
 if (Full (pstack)) return 0;
 pstack->top++;
 pstack->elements[pstack->top] = x;
 return 1;
}


