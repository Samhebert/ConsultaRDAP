import requests
import json
from dotmap import DotMap
from datetime import datetime
import re
import argparse

parser = argparse.ArgumentParser(description="Script verifica a data de vencimento dos dominios usando RDAP.")

parser.add_argument("caminhoArquivosDominios", type=str, help="Caminho do arquivo .txt com os dominios a serem consultados")
parser.add_argument("meses", type=int, help="Quantidade de meses restante para o vencimento")


with open("DominiosPertoVencer.txt", "w") as file:
            file.write("Relatorio \n")

with open("DominiosErros.txt", "w") as file:
            file.write("Relatorio Erros \n")


with open("RelatoriosDominios.txt", "w") as file:
            file.write("Relatorio Completo \n")


def LogStatusDominio(json):
    data = DotMap(json)

    if len(data.events) >= 3:
        dataVencimento = data.events[2].eventDate
        dataVencimento = dataVencimento.split("T")[0]
        dataVencimentoDominio = datetime.strptime(dataVencimento, "%Y-%m-%d")

        tempoVencimento = dataVencimentoDominio - datetime.now()
        tempoVencimento_str = str(tempoVencimento)
        tempoVencimento_str = tempoVencimento_str.split(",")[0]

        TempoVencimento_int = int(tempoVencimento_str.split("d")[0])
    else:
        dataVencimento = "Nao definio data de vencimento"
        tempoVencimento_str = "Nao definido tempo faltante"
        TempoVencimento_int = 0

   
    texto = data.handle + ' , ' + dataVencimento + ' , ' + tempoVencimento_str + ' , ' +  data.status[0] + '\n'

    if TempoVencimento_int <= diasAviso:
        with open("DominiosPertoVencer.txt", "a") as file:
            file.write(texto)

    with open("RelatoriosDominios.txt", "a") as file:
        file.write(texto) 

def GetDominios(conteudoArquivo):
    regex = r"^(?!\d+\.$)([\w\-]{1,63}\.[\w\.\-]+)$"
    lista = re.findall(regex, conteudoArquivo)

    return lista

def FazerRequisicao(dominio):
    print(dominio)
    response = requests.get(dominio)

    if response.status_code == 200:
        LogStatusDominio(response.json())
    else:
        print(f"Erro na requisição: {response.status_code}")

        with open("DominiosErros.txt", "a") as file:
            file.write(f"Erro na requisição: {response.status_code} , Dominio com erro: {dominio} \n")

        with open("RelatoriosDominios.txt", "a") as file:
            file.write(f"Erro na requisição: {response.status_code} , Dominio com erro: {dominio} \n")   


url = 'https://rdap.registro.br/domain/'

args = parser.parse_args()

caminhoDominio = args.caminhoArquivosDominios
dataDeAviso = args.meses

diasAviso = int(dataDeAviso) * 30

with open(caminhoDominio, "r") as file:
     for linha in file:
        listaDominio = GetDominios(linha)
        for dominio in listaDominio:
            FazerRequisicao(url + dominio)
