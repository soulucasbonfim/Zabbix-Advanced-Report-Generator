# Zabbix-Advanced-Report-Generator

![Versão](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/Python-3.9+-brightgreen)
![Licença](https://img.shields.io/badge/license-MIT-green)

Uma aplicação de desktop desenvolvida em Python com PyQt6 para conectar-se à API do Zabbix e gerar relatórios mensais completos em formato Excel. A ferramenta automatiza a coleta de problemas, ações, e calcula análises de SLA, apresentando os dados em planilhas e gráficos detalhados.

[IMAGEM_DA_INTERFACE_PRINCIPAL.png]
<img width="796" height="728" alt="image" src="https://github.com/user-attachments/assets/14a20165-4fe2-4971-8c40-500cb5f90efc" />



## ✨ Recursos

* **Interface Gráfica Intuitiva:** Fácil de usar, permitindo configurar a conexão e os parâmetros do relatório rapidamente.
* **Relatórios Completos em Excel:** Exporta múltiplas planilhas, incluindo:
    * Lista detalhada de problemas.
    * Registro de todas as ações de reconhecimento (acknowledges).
    * Análise de SLA de reconhecimento.
    * Volume diário de eventos e performance de SLA.
    * Rankings de "Top 10 Problemas" e produtividade por usuário.
* **Dashboards Visuais:** Gera uma aba de "Dashboard" no Excel com gráficos automáticos sobre a performance mensal do SLA.
* **Suporte a Múltiplos Idiomas:** A interface e os relatórios são traduzidos automaticamente para Português (pt_BR) e Inglês (en_US) com base no idioma do sistema operacional.
* **Sistema de Atualização Automática:** A aplicação pode verificar se há novas versões disponíveis e realizar a atualização de forma automática.

## 🚀 Como Usar

1.  **Download:** Baixe a versão mais recente (`ZabbixAdvancedReportGenerator.exe`) na seção de [Releases](https://github.com/soulucasbonfim/Zabbix-Advanced-Report-Generator/releases) deste repositório.
2.  **Execução:** Execute o arquivo `.exe`. Nenhuma instalação é necessária.
3.  **Configuração da Conexão:**
    * **URL da API Zabbix:** Insira a URL completa do seu servidor Zabbix (ex: `https://zabbix.suaempresa.com/api_jsonrpc.php`).
    * **Token da API Zabbix:** Gere um token de API no seu perfil de usuário do Zabbix e cole-o aqui.
4.  **Seleção do Período:**
    * Escolha o **Ano** e o **Mês** para o qual o relatório será gerado.
5.  **Configurações do Relatório:**
    * **SLA para Acknowledgement:** Defina o tempo máximo (em minutos) que sua equipe tem para reconhecer um problema.
    * **Filtro de Severidade:** Marque as severidades de problemas que devem ser incluídas no relatório.
6.  **Geração:**
    * Clique em **Gerar Relatório**. O progresso será exibido no console de logs na parte inferior da janela.
    * Ao final, o relatório em Excel será salvo na pasta `Zabbix Reports` dentro da sua pasta de usuário, e uma mensagem de sucesso será exibida.

[IMAGEM_DO_RELATORIO_EXCEL.png]
*(Dica: Tire um print de uma parte do relatório gerado no Excel e adicione aqui)*

## ⚙️ Configuração do Atualizador

Para que a verificação de novas versões funcione, a aplicação precisa saber onde procurar. Esta configuração está no código, no arquivo `updater.py`:

```python
VERSION_URL = "[https://raw.githubusercontent.com/soulucasbonfim/Zabbix-Advanced-Report-Generator/main/version.json](https://raw.githubusercontent.com/soulucasbonfim/Zabbix-Advanced-Report-Generator/main/version.json)"
```

## 👨‍💻 Desenvolvido por

* **Lucas Bonfim de Oliveira Lima**
* **LinkedIn:** [linkedin.com/in/soulucasbonfim](https://www.linkedin.com/in/soulucasbonfim)

---
