#include <stdio.h>
#include <stdlib.h>
#define TREE struct node *

FILE *fp = fopen("rizultat.txt", "w");


struct node
{
int info;
struct node *left, *right;
};

TREE new_node (int x)		//функция создания нового узла
{
TREE ptr;
ptr = (TREE) malloc (sizeof(struct node));
ptr->info = x;
ptr->left = ptr->right = NULL;
return ptr;
}

TREE add_node(int x, TREE pn)	//функция добавления узла в дерево
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

void print_sim (TREE pn)	//функция печати дерева в симметричном порядке
{
if (pn->left)
print_sim (pn->left);
printf ("%d ",pn->info);
fprintf (fp,"%d ",pn->info);
if (pn->right)
print_sim (pn->right);
}

void del_tree(TREE pn)	//функция удаления дерева
{
if (pn->left)
del_tree(pn->left);
if (pn->right)
del_tree(pn->right);
free (pn);
}

void Del (TREE *q, TREE *r);	//вспомогательная функция для удаления узла с обоими сыновьями
void Delete (TREE *p, int x)	//функция удаления узла со значением х из дерева
{
	TREE q;
	if (*p==NULL) {	 return;}
    if (x<(*p)->info)
		Delete (&(*p)->left, x);	//ищем в левом поддереве
	else
		if (x>(*p)->info)
			Delete (&(*p)->right, x);	//ищем в правом поддереве
		else					//нашли
		{
			q = *p;
			if ((*p)->left==NULL)	//нет левого сына
				*p = (*p)->right;		// "поднимаем" правого
			else
				if ((*p)->right==NULL)		//нет правого сына
					*p=(*p)->left;		// "поднимаем" левого
				else 			//есть оба сына
					Del (&q, &(*p)->right);
	        free (q);
         }
}
void Del (TREE *q, TREE *r)
{
	if ((*r)->left)
		Del (q, &(*r)->left);	//добираемся до самой левой компоненты
	else
	{
		(*q)->info = (*r)->info;	//переписываем информационное поле в удаляемый элемент
		*q = *r;	//переставляем указатель на освободившийся элемент, чтобы освободить память
		*r = (*r)->right;	// "поднимаем" правого сына переставленного узла
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
