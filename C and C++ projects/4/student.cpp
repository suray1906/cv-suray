#include <iostream>
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
# include <cstring>
# include <windows.h>
#include <locale>
# define nam 200 //Название пункта
# define zap 200 //Кол-во структур
int er; //Переключатель
using namespace std;

struct student
{
char name[nam]; //продолжительность
int date; //Время
int dat; //Время
};

struct student mas_student[zap];
struct student bad;
int sch=0; //Счетчик полных записей

void enter_new() // ф-ция ввода новой структуры
{
if(sch<zap)
{
cout<<"Запись номер";cout<<sch+1;
cout<< endl<<"Введите имя"<<endl;
cin>>mas_student[sch].name;
cout<<"Введите дату поступления"<<endl;
cin>>mas_student[sch].date;
cout<<"Введите дату отчисления "<<endl;
cin>>mas_student[sch].dat;
sch++;
}
else {cout<<"Введено максимальное кол-во записей";}

cout<<"Что делать дальше? Введите цифру из меню при необходимости"<<endl;
cin>>er;
}

void del() //ф-ция удаления записи
{ int d; //номер записи, которую нужно удалить
cout<<"\nВведите номер записи, которую необходимо удалить"<<endl;
cout<<"Если необходимо удалить все записи,нажмите '99'"<<endl;
cin>>d;
if (d!=99)
{for (int de_1=(d-1);de_1<sch;de_1++)
mas_student[de_1]=mas_student[de_1+1];
sch=sch-1;
}
if (d==99)
for(int i=0;i<zap;i++)
mas_student[i]=bad;
cout<<"Что делать дальше?"<<endl;
cin>>er;
}

void change()
{int c; //номер записи, которую нужно изменить
int per;
cout<<"\nВведите номер записи"<<endl;
cin>> c;
do
{
cout<<"Введите: "<<endl;
cout<<"1-для изменения имени"<<endl;
cout<<"2-для изменения даты поступления"<<endl;
cout<<"3-для изменения даты отчисления"<<endl;
cout<<"4-для прекращения\n";
cin>>per;
switch (per)
{
case 1: cout<<"Введите новое имя ";cin>>mas_student[c-1].name;
break;
case 2: cout<<"Введите новую дату поступления ";cin>>mas_student[c-1].date;
break;
case 3: cout<<"Введите новое дату отчисления ";cin>>mas_student[c-1].dat;
break;
cin>>per;
}
}while(per!=4);
cout<<"Что делать дальше?"<<endl;
cin>>er;
}

void out() //ф-ция вывода записей
{
int sw; // переключатель
int o; //номер структ, кот. надо вывести
cout<<endl<<"Введите: "<<endl;
cout<<"1-если хотите вывести какую-либо запсь"<<endl;
cout<<"2-если хотите вывести все записи"<<endl;
cin>>sw;
if(sw==1)
{
cout<<"Введите номер записи, которую нужно вывести"<<endl;
cin>>o;
cout<<endl;
cout<<"имя";cout<<mas_student[o-1].name<<endl;
cout<<"дата поступления";cout<<mas_student[o-1].date<<endl;
cout<<"дата отчисления";cout<<mas_student[o-1].dat<<endl;
}
if(sw==2)
{ for(int i=0;i<sw;i++)
{
cout<<"имя";cout<<mas_student[i].name<<endl;
cout<<"дату поступления";cout<<mas_student[i].date<<endl;
cout<<"дату отчисления";cout<<mas_student[i].dat<<endl;
}
}
cout<<"Что делать дальше?"<<endl;
cin>>er;
}
int main()
{
setlocale(LC_CTYPE, "Russian");
cout<<"Записей пока нет"<<endl;
cout<<"Введите:"<<endl;
cout<<"1-для удаления записи"<<endl;
cout<<"2-для ввода новой записи"<<endl;
cout<<"3-для изменения записи"<<endl;
cout<<"4-для вывода записи(ей)"<<endl;
cout<<"5-для выхода"<<endl;
cin>>er;
do
{switch(er)
{
case 1:del();break;
case 2:enter_new();break;
case 3:change();break;
case 4:out();break;
}
}
while(er!=5);
}
