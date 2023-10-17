from datetime import datetime
import random
from flask import Blueprint, jsonify, request
import requests
import pandas as pd
import mpmath as mp
import numpy as np
import statistics
from openpyxl import load_workbook



def process_json():
    request_data = request.get_json()  # Mendapatkan data JSON dari permintaan POST
    sample = []
    noreg =[]
    yakin =[]
    nilaicareless = []
    nilaibeda = []
    success_data = []

    for i in range(len(request_data)):
        sample_isi = []
        
        noreg.append(request_data[i][f"c_Internal"])
        for j in range(len(request_data[0].keys())-1):
            key = f"c_N{str(j + 1)}"
            if key in request_data[i]:
                sampledata = request_data[i][key]
            else:
                sampledata = '0'
            intdata = int(sampledata)
            sample_isi.append(intdata)
        sample.append(sample_isi)
         
        num_student = len(sample)
        num_soal = len(sample[0])
       
        
    for i in range(num_soal):
            # Menghitung jumlah benar tiap nomor
        success_count = sum(sample[i] == 1 for sample in sample)
        success_data.append(success_count)
            # Menghitung tingkat kesulitan tiap soal
    successratio=[(success_data[j]/num_student) for j in range(num_soal)]

        # Menghitung total jawaban benar untuk setiap siswa
    student_correct_counts = [sum(sample[i]) for i in range(num_student)]
        # Mengurutkan siswa berdasarkan total jawaban benar
    sorted_students = sorted(range(num_student), key=lambda i: student_correct_counts[i], reverse=True)
        # Menghitung jumlah siswa terbaik dan terburuk
    selected_students_count = int(0.30 * num_student)
    top_students = sorted_students[:selected_students_count]
    bottom_students = sorted_students[-selected_students_count:]
        # Menghitung total jawaban benar per soal untuk siswa terbaik
    correct_answers_top_students = [sum(sample[i][j] for i in top_students) for j in range(num_soal)]
        # Menghitung total jawaban benar per soal untuk siswa terburuk
    correct_answers_bottom_students = [sum(sample[i][j] for i in bottom_students) for j in range(num_soal)]
        # Menghitung daya beda per soal
        

    for i in range(num_soal):
        hitung_pa = correct_answers_top_students[i] / selected_students_count
        hitung_pb = correct_answers_bottom_students[i] / selected_students_count
        hitung_beda = (hitung_pa - hitung_pb) if (hitung_pa - hitung_pb) != 0 else 0.01
        nilaibeda.append(hitung_beda)
            
    nilaiguess = 0.2
    awal = [sum(sample[i]) / num_soal for i in range(num_student)]
    probawal=[]
    for i in range(num_student):
        prob_1 = []
        for j in range(num_soal):
            e = np.exp(-1*nilaibeda[j]*(awal[i]-successratio[j]))
            hitung_prob = nilaiguess+((1-nilaiguess)/(1+e))
            prob_1.append(hitung_prob)
        probawal.append(prob_1)
    iterasi = 10
    for i in range(num_student) :
     awalcalc = awal[i]
    for _ in range (iterasi):
        awalatas = []
        awalbawah = []
        for j in range(num_soal):
         probcalc = probawal[i][j]
        responsiswa = sample[i][j]
        atas = nilaibeda[j]*(responsiswa-probcalc)
        bawah = (nilaibeda[j]**2)*(probcalc-(1-probcalc))
        if responsiswa == 0 :
            atas = 0
            bawah = 1
        awalatas.append(atas)
        awalbawah.append(bawah)
        awalhitung = sum(awalatas)/sum(awalbawah)
        jumlahawal = awalcalc+(awalhitung)
        if abs(awalhitung) < 0.009:
         break
        awal[i]= jumlahawal
        for j in range (num_soal):
         e = np.exp((-1 * nilaibeda[j] * (awal[i] - successratio[j])))
        probawal[i][j]= nilaiguess + ((1 - nilaiguess) * (1 / (1 + e)))
    
    totalarray = []
    for i in range(len(probawal)):
        total_score = sum(probawal[i])/num_soal
        totalarray.append(total_score)
    nilairata = sum(totalarray)/num_student

    nilaiakhir = []
    data = np.array(totalarray)
    std =np.std(data)

    standard_data = [float(i) for i in totalarray]
    rerata = statistics.mean(standard_data)
    list_varian = []
    for bilangan in data:
        list_varian.append(
            (bilangan - rerata) ** 2
        )

    
    for i in range(num_student):
        nilaiakhirhitung = 500+(100*(totalarray[i]-nilairata)/std)
        nilaiakhir.append(nilaiakhirhitung)

    data = {'noreg': noreg, 'nilai_akhir': nilaiakhir}

    return jsonify({'message': data})