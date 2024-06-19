#include <iostream>
#include <cstdlib>
#include <string>

using namespace std;
// �������� ��������� ��� ������ ����������
struct StudentRecord {
string firstName;
string dateOfin;
string dateOfout;
int oduUin;
StudentRecord *next;
};
StudentRecord *head = NULL;

void free_list()
{
    // �� �������� ������� ���� � �������� ��� ���������, ����� �� ��������� ���� ����� ��������� ������ � ������ ��� ������, ���������� � ��������� ������
StudentRecord *current = head;
while(current!=NULL) // tail->next = NULL
{
    head->next = current->next;
    current->next = NULL;
    free(current);
    current = head->next;
}

head = NULL;
}


void display_data()
{
cout << endl << endl << "���� ������ " << endl;
cout << "---------------------------" << endl;
// �� �������� ���� � ������ start � ����� ���������� ��� �� ����� ���������� ������ � ���������� ������
StudentRecord *start = head;
if (!start) {
cout << "No Data!" << endl;
return;
}
while(start) {
cout << start -> firstName << endl;
cout << start -> dateOfin << endl;
cout << start -> dateOfout << endl;
cout << start -> oduUin << endl;

start = start -> next;
}
}



StudentRecord *get_data()
{
     // �������� ���������� ����, � ������� �� ����� ������� ��� ������ ��������� � ������� ��������� ���� � ����� �������
StudentRecord *rec = new StudentRecord;
cout << endl;
cout << "�� ������� 1" << endl;
cout << "������� ��� ";
cin >> rec->firstName;
cout << "������� ���� ���������� ";
cin >> rec->dateOfin;
cout << "������� ���� ���������� ";
cin >> rec->dateOfout;
cout << "������� ���������� ����� ";
cin >> rec->oduUin;
rec->next = head;
return rec;
}

void add_data(StudentRecord *current)
{
// �� �������� ����� �������� ��������� ���� � ��������� ���� �������� ����, � ����� ������� ������� ���� ��������
current->next=head;  // ��������� ����� ��������� ��������� (������ ����)
head = current;

}

void search(double key)
{
     // �� ����� ���������� ��������� ���������� ������ �� ��� ���, ���� �� ������ ��������� ���������� ��� �� ����� ���������� ������
    while (head != NULL)
    {
        if (head->oduUin == key)
        {
            cout<<"key found"<<endl;
           // cout<<head->uin<<endl;
            cout<<"��� =  "<<head->firstName<<endl;
            cout<<"���� ���������� = "<<head->dateOfin<<endl;
            cout<<"���� ���������� = "<<head->dateOfout<<endl;
            return;
        }
        head = head->next;
    }
    cout<<"Key not found"<<endl;
}

void processMenu()
{
     // �������� �������� ���� ��� ��������� StudentRecord
StudentRecord *current = NULL;
int ser;
char choice = 0;
while(true) {
cout << endl <<"�������� �����" << endl;
cout <<"==========================" << endl;
cout << "1. ������ ������ " << endl;
cout << "2. ������� ��� ������ " << endl;
cout << "3. ����� " <<endl;
cout << "4. ����� " << endl;

cin >> choice;
while(cin.get() != '\n');
if(choice == '1'){
current = get_data();
add_data(current);
}
else if(choice == '2'){
display_data();
}
else if (choice == '3'){
free_list();
return;
}
else if (choice == '4'){
    cout<<"������� ����� ��������"<<endl;
    cin>>ser;
search(ser);
}
else {
cout << "�� ������ �� ����" << endl;
}
}
}

int main()
{
    setlocale(LC_CTYPE, "Russian");

cout << "����� ����������!!!!!!!!!!!!" << endl << endl;
processMenu();
system("pause");
return 0;
}
