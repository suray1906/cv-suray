#include <iostream>
#include <cstdlib>
#include <string>

using namespace std;
// создание структуры для записи информации
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
    // Мы создадим текущий узел и назначим ему заголовок, затем мы переберем узел через связанный список и удалим все записи, хранящиеся в связанном списке
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
cout << endl << endl << "Весь список " << endl;
cout << "---------------------------" << endl;
// Мы создадим узел с именем start и будем перебирать его по всему связанному списку и отображать данные
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
     // создание временного узла, в котором мы будем хранить все записи студентов и вернуть временный узел в конце функции
StudentRecord *rec = new StudentRecord;
cout << endl;
cout << "Вы выбрали 1" << endl;
cout << "Введите ФИО ";
cin >> rec->firstName;
cout << "Введите дату зачисления ";
cin >> rec->dateOfin;
cout << "Введите дату отчисления ";
cin >> rec->dateOfout;
cout << "Введите порядковый номер ";
cin >> rec->oduUin;
rec->next = head;
return rec;
}

void add_data(StudentRecord *current)
{
// Мы сохраним адрес текущего головного узла в следующем поле текущего узла, а позже сделаем текущий узел головным
current->next=head;  // сохраняем адрес заголовка указателя (второе поле)
head = current;

}

void search(double key)
{
     // Мы будем перебирать заголовок связанного списка до тех пор, пока не найдем требуемую переменную или до конца связанного списка
    while (head != NULL)
    {
        if (head->oduUin == key)
        {
            cout<<"key found"<<endl;
           // cout<<head->uin<<endl;
            cout<<"ФИО =  "<<head->firstName<<endl;
            cout<<"Дата зачисления = "<<head->dateOfin<<endl;
            cout<<"Дата отчисления = "<<head->dateOfout<<endl;
            return;
        }
        head = head->next;
    }
    cout<<"Key not found"<<endl;
}

void processMenu()
{
     // создание текущего узла для структуры StudentRecord
StudentRecord *current = NULL;
int ser;
char choice = 0;
while(true) {
cout << endl <<"Выберите опцию" << endl;
cout <<"==========================" << endl;
cout << "1. Ввести данные " << endl;
cout << "2. Вывести все данные " << endl;
cout << "3. Выход " <<endl;
cout << "4. Поиск " << endl;

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
    cout<<"Введите номер студента"<<endl;
    cin>>ser;
search(ser);
}
else {
cout << "Вы нажали не туда" << endl;
}
}
}

int main()
{
    setlocale(LC_CTYPE, "Russian");

cout << "Добро пожаловать!!!!!!!!!!!!" << endl << endl;
processMenu();
system("pause");
return 0;
}
