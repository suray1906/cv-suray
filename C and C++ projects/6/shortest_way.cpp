#include <iostream>
using namespace std;
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#define SIZE 12


int main()
{
  setlocale (LC_ALL, "Russian");
  int DUG[SIZE][SIZE]; // матрица связей
  int MIN_WEG[SIZE]; // минимальное расстояние
  int FIKS[SIZE]; // посещенные вершины
  int temp, minindex, min;
  int begin_index = 0;
  system("chcp 1251");
  system("cls");
  // Инициализация матрицы связей
  FILE *fp = fopen("rizultat.txt", "w");


  for (int i = 0; i<SIZE; i++)
  {
    DUG[i][i] = 0;
    for (int j = i + 1; j<SIZE; j++) {
      printf("Введите расстояние %d - %d: ", i + 1, j + 1);
      fprintf(fp,"Введите расстояние %d - %d: \n", i + 1, j + 1);
      scanf("%d", &temp);
      fprintf(fp,"%d \n",temp);
      DUG[i][j] = temp;
      DUG[j][i] = temp;
    }
  }
  // Вывод матрицы связей
  for (int i = 0; i<SIZE; i++)
  {
    for (int j = 0; j<SIZE; j++)
      {printf("%5d ", DUG[i][j]);
      fprintf(fp, "%5d ", DUG[i][j]);}
    printf("\n");
  }
  //Инициализация вершин и расстояний
  for (int i = 0; i<SIZE; i++)
  {
    MIN_WEG[i] = 10000;
    FIKS[i] = 1;
  }
  MIN_WEG[begin_index] = 0;
  // Шаг алгоритма
  do {
    minindex = 10000;
    min = 10000;
    for (int i = 0; i<SIZE; i++)
    { // Если вершину ещё не обошли и вес меньше min
      if ((FIKS[i] == 1) && (MIN_WEG[i]<min))
      { // Переприсваиваем значения
        min = MIN_WEG[i];
        minindex = i;
      }
    }
    // Добавляем найденный минимальный вес
    // к текущему весу вершины
    // и сравниваем с текущим минимальным весом вершины
    if (minindex != 10000)
    {
      for (int i = 0; i<SIZE; i++)
      {
        if (DUG[minindex][i] > 0)
        {
          temp = min + DUG[minindex][i];
          if (temp < MIN_WEG[i])
          {
            MIN_WEG[i] = temp;
          }
        }
      }
      FIKS[minindex] = 0;
    }
  } while (minindex < 10000);
  // Вывод кратчайших расстояний до вершин
  printf("\nКратчайшие расстояния до вершин: \n");
  fprintf(fp, "\nКратчайшие расстояния до вершин: \n");
  for (int i = 0; i<SIZE; i++)
   {printf("%5d ", MIN_WEG[i]);
    fprintf(fp,"%5d ", MIN_WEG[i]);
   }
  // Восстановление пути
  int ver[SIZE]; // массив посещенных вершин
  int end = 4; // индекс конечной вершины = 5 - 1
  ver[0] = end + 1; // начальный элемент - конечная вершина
  int k = 1; // индекс предыдущей вершины
  int weight = MIN_WEG[end]; // вес конечной вершины

  while (end != begin_index) // пока не дошли до начальной вершины
  {
    for (int i = 0; i<SIZE; i++) // просматриваем все вершины
      if (DUG[i][end] != 0)   // если связь есть
      {
        int temp = weight - DUG[i][end]; // определяем вес пути из предыдущей вершины
        if (temp == MIN_WEG[i]) // если вес совпал с рассчитанным
        {                 // значит из этой вершины и был переход
          weight = temp; // сохраняем новый вес
          end = i;       // сохраняем предыдущую вершину
          ver[k] = i + 1; // и записываем ее в массив
          k++;
        }
      }
  }
  // Вывод пути (начальная вершина оказалась в конце массива из k элементов)
  printf("\nВывод кратчайшего пути\n");
  fprintf(fp, "\nВывод кратчайшего пути\n");
  for (int i = k - 1; i >= 0; i--)
   {
       printf("%3d ", ver[i]);
    fprintf(fp, "%3d ", ver[i]);

   }
  getchar(); getchar();
  fclose(fp);
  return 0;
}
