#include <iostream>
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
# include <cstring>
# include <windows.h>
#include <locale>
# define nam 200 //�������� ������
# define zap 200 //���-�� ��������
int er; //�������������
using namespace std;

struct student
{
char name[nam]; //�����������������
int date; //�����
int dat; //�����
};

struct student mas_student[zap];
struct student bad;
int sch=0; //������� ������ �������

void enter_new() // �-��� ����� ����� ���������
{
if(sch<zap)
{
cout<<"������ �����";cout<<sch+1;
cout<< endl<<"������� ���"<<endl;
cin>>mas_student[sch].name;
cout<<"������� ���� �����������"<<endl;
cin>>mas_student[sch].date;
cout<<"������� ���� ���������� "<<endl;
cin>>mas_student[sch].dat;
sch++;
}
else {cout<<"������� ������������ ���-�� �������";}

cout<<"��� ������ ������? ������� ����� �� ���� ��� �������������"<<endl;
cin>>er;
}

void del() //�-��� �������� ������
{ int d; //����� ������, ������� ����� �������
cout<<"\n������� ����� ������, ������� ���������� �������"<<endl;
cout<<"���� ���������� ������� ��� ������,������� '99'"<<endl;
cin>>d;
if (d!=99)
{for (int de_1=(d-1);de_1<sch;de_1++)
mas_student[de_1]=mas_student[de_1+1];
sch=sch-1;
}
if (d==99)
for(int i=0;i<zap;i++)
mas_student[i]=bad;
cout<<"��� ������ ������?"<<endl;
cin>>er;
}

void change()
{int c; //����� ������, ������� ����� ��������
int per;
cout<<"\n������� ����� ������"<<endl;
cin>> c;
do
{
cout<<"�������: "<<endl;
cout<<"1-��� ��������� �����"<<endl;
cout<<"2-��� ��������� ���� �����������"<<endl;
cout<<"3-��� ��������� ���� ����������"<<endl;
cout<<"4-��� �����������\n";
cin>>per;
switch (per)
{
case 1: cout<<"������� ����� ��� ";cin>>mas_student[c-1].name;
break;
case 2: cout<<"������� ����� ���� ����������� ";cin>>mas_student[c-1].date;
break;
case 3: cout<<"������� ����� ���� ���������� ";cin>>mas_student[c-1].dat;
break;
cin>>per;
}
}while(per!=4);
cout<<"��� ������ ������?"<<endl;
cin>>er;
}

void out() //�-��� ������ �������
{
int sw; // �������������
int o; //����� ������, ���. ���� �������
cout<<endl<<"�������: "<<endl;
cout<<"1-���� ������ ������� �����-���� �����"<<endl;
cout<<"2-���� ������ ������� ��� ������"<<endl;
cin>>sw;
if(sw==1)
{
cout<<"������� ����� ������, ������� ����� �������"<<endl;
cin>>o;
cout<<endl;
cout<<"���";cout<<mas_student[o-1].name<<endl;
cout<<"���� �����������";cout<<mas_student[o-1].date<<endl;
cout<<"���� ����������";cout<<mas_student[o-1].dat<<endl;
}
if(sw==2)
{ for(int i=0;i<sw;i++)
{
cout<<"���";cout<<mas_student[i].name<<endl;
cout<<"���� �����������";cout<<mas_student[i].date<<endl;
cout<<"���� ����������";cout<<mas_student[i].dat<<endl;
}
}
cout<<"��� ������ ������?"<<endl;
cin>>er;
}
int main()
{
setlocale(LC_CTYPE, "Russian");
cout<<"������� ���� ���"<<endl;
cout<<"�������:"<<endl;
cout<<"1-��� �������� ������"<<endl;
cout<<"2-��� ����� ����� ������"<<endl;
cout<<"3-��� ��������� ������"<<endl;
cout<<"4-��� ������ ������(��)"<<endl;
cout<<"5-��� ������"<<endl;
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
