#include <stdio.h>
#include <stdlib.h>
#define TREE struct node *

FILE *fp = fopen("rizultat.txt", "w");


struct node
{
int info;
struct node *left, *right;
};

TREE new_node (int x)		//������� �������� ������ ����
{
TREE ptr;
ptr = (TREE) malloc (sizeof(struct node));
ptr->info = x;
ptr->left = ptr->right = NULL;
return ptr;
}

TREE add_node(int x, TREE pn)	//������� ���������� ���� � ������
{
TREE ptr = pn;
if (pn == NULL)
return new_node (x);
if (x < pn->info)
pn->left = add_node (x, pn->left);
else
pn->right = add_node (x, pn->right);
return ptr;
}

void print_sim (TREE pn)	//������� ������ ������ � ������������ �������
{
if (pn->left)
print_sim (pn->left);
printf ("%d ",pn->info);
fprintf (fp,"%d ",pn->info);
if (pn->right)
print_sim (pn->right);
}

void del_tree(TREE pn)	//������� �������� ������
{
if (pn->left)
del_tree(pn->left);
if (pn->right)
del_tree(pn->right);
free (pn);
}

void Del (TREE *q, TREE *r);	//��������������� ������� ��� �������� ���� � ������ ���������
void Delete (TREE *p, int x)	//������� �������� ���� �� ��������� � �� ������
{
	TREE q;
	if (*p==NULL) {	 return;}
    if (x<(*p)->info)
		Delete (&(*p)->left, x);	//���� � ����� ���������
	else
		if (x>(*p)->info)
			Delete (&(*p)->right, x);	//���� � ������ ���������
		else					//�����
		{
			q = *p;
			if ((*p)->left==NULL)	//��� ������ ����
				*p = (*p)->right;		// "���������" �������
			else
				if ((*p)->right==NULL)		//��� ������� ����
					*p=(*p)->left;		// "���������" ������
				else 			//���� ��� ����
					Del (&q, &(*p)->right);
	        free (q);
         }
}
void Del (TREE *q, TREE *r)
{
	if ((*r)->left)
		Del (q, &(*r)->left);	//���������� �� ����� ����� ����������
	else
	{
		(*q)->info = (*r)->info;	//������������ �������������� ���� � ��������� �������
		*q = *r;	//������������ ��������� �� �������������� �������, ����� ���������� ������
		*r = (*r)->right;	// "���������" ������� ���� ��������������� ����
	}
}

main()
{
TREE t=NULL;
int mas[] = {21, 10, 19, 99, 25, 88, 20, 10, 91, 63, 45, 56, 76}, i;
for(i=0; i<13; i++)
t = add_node(mas[i], t);
print_sim (t); printf("\n");

del_tree(t);
system("pause");
return 0;
}
