# Zabbix Report Suite

![Versão](https://img.shields.io/badge/version-4.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.9+-brightgreen)
![Licença](https://img.shields.io/badge/license-MIT-green)

Uma suíte profissional de desktop desenvolvida em Python e PyQt6 para conectar-se à API do Zabbix e gerar relatórios avançados em formato Excel. A ferramenta automatiza a coleta de problemas, calcula análises de SLA (TTA/TTR) e extrai inventário de hosts, oferecendo planilhas e dashboards visuais.

[IMAGEM_DA_INTERFACE_PRINCIPAL.png]
<img width="894" height="777" alt="image" src="https://github.com/user-attachments/assets/c36d1141-a524-4a03-859a-5e3827619023" />


## ✨ Recursos Principais (v4.0.0)

### 1. Relatórios Avançados e Métricas
* **Análise de SLA Detalhada (TTA/TTR):** Gera métricas de Tempo para Reconhecimento (TTA) e **Tempo para Resolução (TTR)**, comparando resultados com metas configuráveis por severidade.
* **Novo Relatório de Inventário:** Extrai dados de hosts, incluindo informações detalhadas do **Inventário Zabbix** (OS, Hardware), interfaces (IP/DNS) e métricas de performance (Uptime, Load, Memória).
* **Dashboards Visuais:** Cria uma aba de **Dashboard** no Excel com gráficos de tendências diárias e resumos mensais da performance do SLA (TTA).
* **Filtros de Data Flexíveis:** Permite selecionar períodos específicos e incluir filtros avançados, como **Horário Comercial** e **Ignorar Manutenções**.

### 2. Arquitetura e Usabilidade
* **Múltiplos Perfis de Cliente:** Permite criar, salvar, editar e excluir **múltiplos perfis** com diferentes URLs, Tokens, Metas de TTA/TTR e Mapeamentos de Prioridade (útil para consultorias e MSPs).
* **Criptografia de Token:** O token da API é criptografado usando o **Windows DPAPI** para garantir o armazenamento seguro das credenciais por usuário.
* **Suporte a Múltiplos Idiomas:** A interface e os relatórios são traduzidos automaticamente para **Português (pt\_BR)** e **Inglês (en\_US)** com base no idioma do sistema operacional.
* **Temas Claro e Escuro:** Suporte a personalização visual da aplicação.
* **Processamento em Segundo Plano:** Todas as chamadas à API e a geração de relatórios são executadas em **threads separadas** para garantir que a interface gráfica não congele.

### 3. Conteúdo do Relatório SLA (Excel)
O relatório consolidado agora exporta as seguintes planilhas (selecionáveis na aba de **Saída**):
* Lista detalhada de **Problemas**.
* Registro de todas as **Ações de Reconhecimento** (*acknowledges*).
* **Detalhes TTA** (Tempo de Reconhecimento) e **Detalhes TTR** (Tempo de Resolução).
* Resumo Diário TTA, Volume Diário de Eventos, Top 10 Problemas e Produtividade do Usuário.

## 🚀 Como Usar

1.  **Download:** Baixe a versão mais recente (`ZabbixAdvancedReportGenerator.exe`) na seção de [Releases](https://github.com/soulucasbonfim/Zabbix-Advanced-Report-Generator/releases) deste repositório.
2.  **Execução:** Execute o arquivo `.exe`. Nenhuma instalação é necessária.
3.  **Configuração (Novo Fluxo):**
    * Vá para a aba **Configurações**.
    * Clique em **Criar Novo** e defina um nome para o perfil (ex: "Cliente A").
    * Insira a **URL da API Zabbix** e o **Token da API Zabbix**.
    * Clique em **Testar Conexão** e, em seguida, **Salvar Perfil**.
4.  **Definindo Metas:**
    * Nas abas **SLA (TTA)** e **Resolução (TTR)**, configure as metas de tempo (em minutos) e o mapeamento das severidades Zabbix para nomes de Prioridade do seu cliente.
5.  **Geração do Relatório:**
    * Vá para a aba **Análise de SLA** ou **Inventário de Hosts**.
    * Selecione o **Perfil Ativo** no menu superior.
    * Defina os filtros (período, grupos de hosts, etc.).
    * Clique em **Gerar Relatório**. O progresso será exibido no console de logs inferior.
    * O relatório em Excel será salvo no diretório de saída configurado.

[IMAGEM_DO_RELATORIO_EXCEL.png]
<img width="1444" height="624" alt="image" src="https://github.com/user-attachments/assets/ab42571c-e8a4-4645-970a-fe828f9392f2" />


## ⚙️ Configuração do Atualizador

O sistema de atualização automática busca o arquivo de configuração no seguinte local:

```python
VERSION_URL = "[https://raw.githubusercontent.com/soulucasbonfim/Zabbix-Advanced-Report-Generator/main/version.json](https://raw.githubusercontent.com/soulucasbonfim/Zabbix-Advanced-Report-Generator/main/version.json)"

## 👨‍💻 Desenvolvido por

* **Lucas Bonfim de Oliveira Lima**
* **LinkedIn:** [linkedin.com/in/soulucasbonfim](https://www.linkedin.com/in/soulucasbonfim)

---
