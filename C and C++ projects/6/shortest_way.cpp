#include <iostream>
using namespace std;
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#define SIZE 12


int main()
{
  setlocale (LC_ALL, "Russian");
  int DUG[SIZE][SIZE]; // ������� ������
  int MIN_WEG[SIZE]; // ����������� ����������
  int FIKS[SIZE]; // ���������� �������
  int temp, minindex, min;
  int begin_index = 0;
  system("chcp 1251");
  system("cls");
  // ������������� ������� ������
  FILE *fp = fopen("rizultat.txt", "w");


  for (int i = 0; i<SIZE; i++)
  {
    DUG[i][i] = 0;
    for (int j = i + 1; j<SIZE; j++) {
      printf("������� ���������� %d - %d: ", i + 1, j + 1);
      fprintf(fp,"������� ���������� %d - %d: \n", i + 1, j + 1);
      scanf("%d", &temp);
      fprintf(fp,"%d \n",temp);
      DUG[i][j] = temp;
      DUG[j][i] = temp;
    }
  }
  // ����� ������� ������
  for (int i = 0; i<SIZE; i++)
  {
    for (int j = 0; j<SIZE; j++)
      {printf("%5d ", DUG[i][j]);
      fprintf(fp, "%5d ", DUG[i][j]);}
    printf("\n");
  }
  //������������� ������ � ����������
  for (int i = 0; i<SIZE; i++)
  {
    MIN_WEG[i] = 10000;
    FIKS[i] = 1;
  }
  MIN_WEG[begin_index] = 0;
  // ��� ���������
  do {
    minindex = 10000;
    min = 10000;
    for (int i = 0; i<SIZE; i++)
    { // ���� ������� ��� �� ������ � ��� ������ min
      if ((FIKS[i] == 1) && (MIN_WEG[i]<min))
      { // ��������������� ��������
        min = MIN_WEG[i];
        minindex = i;
      }
    }
    // ��������� ��������� ����������� ���
    // � �������� ���� �������
    // � ���������� � ������� ����������� ����� �������
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
  // ����� ���������� ���������� �� ������
  printf("\n���������� ���������� �� ������: \n");
  fprintf(fp, "\n���������� ���������� �� ������: \n");
  for (int i = 0; i<SIZE; i++)
   {printf("%5d ", MIN_WEG[i]);
    fprintf(fp,"%5d ", MIN_WEG[i]);
   }
  // �������������� ����
  int ver[SIZE]; // ������ ���������� ������
  int end = 4; // ������ �������� ������� = 5 - 1
  ver[0] = end + 1; // ��������� ������� - �������� �������
  int k = 1; // ������ ���������� �������
  int weight = MIN_WEG[end]; // ��� �������� �������

  while (end != begin_index) // ���� �� ����� �� ��������� �������
  {
    for (int i = 0; i<SIZE; i++) // ������������� ��� �������
      if (DUG[i][end] != 0)   // ���� ����� ����
      {
        int temp = weight - DUG[i][end]; // ���������� ��� ���� �� ���������� �������
        if (temp == MIN_WEG[i]) // ���� ��� ������ � ������������
        {                 // ������ �� ���� ������� � ��� �������
          weight = temp; // ��������� ����� ���
          end = i;       // ��������� ���������� �������
          ver[k] = i + 1; // � ���������� �� � ������
          k++;
        }
      }
  }
  // ����� ���� (��������� ������� ��������� � ����� ������� �� k ���������)
  printf("\n����� ����������� ����\n");
  fprintf(fp, "\n����� ����������� ����\n");
  for (int i = k - 1; i >= 0; i--)
   {
       printf("%3d ", ver[i]);
    fprintf(fp, "%3d ", ver[i]);

   }
  getchar(); getchar();
  fclose(fp);
  return 0;
}
