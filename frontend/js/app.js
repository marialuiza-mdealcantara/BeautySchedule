/**
 * Controlador de Interface (UI) do BeautySchedule.
 * Integra Dashboard, Agenda Diária, Agendamentos, Clientes, Serviços e Relatórios.
 */

document.addEventListener("DOMContentLoaded", () => {
    const state = {
        currentView: "dashboard",
        agendaDate: "2026-11-09",
        clientesAtivos: [],
        servicosAtivos: [],
        todosClientes: [],
        todosServicos: [],
    };

    const VIEW_METADATA = {
        dashboard: {
            title: "Dashboard Operacional",
            subtitle: "Visão consolidada de atendimentos, clientes e serviços do salão",
        },
        agenda: {
            title: "Agenda Diária do Salão",
            subtitle: "Consulte os horários ocupados, vagas disponíveis e expediente por data",
        },
        agendamentos: {
            title: "Administração de Agendamentos",
            subtitle: "Crie, confirme, conclua, reagende ou cancele solicitações recebidas",
        },
        clientes: {
            title: "Cadastro e Histórico de Clientes",
            subtitle: "Gerencie informações de contato, status e histórico de atendimentos",
        },
        servicos: {
            title: "Catálogo de Serviços",
            subtitle: "Administre procedimentos, duração em minutos e preços praticados",
        },
        relatorios: {
            title: "Relatórios e Indicadores",
            subtitle: "Acompanhe o desempenho dos serviços e a movimentação da agenda",
        },
    };

    // Utilitários de Formatação
    function formatCurrency(val) {
        return Number(val || 0).toLocaleString("pt-BR", {
            style: "currency",
            currency: "BRL",
        });
    }

    function formatDateBR(isoDate) {
        if (!isoDate) return "—";
        const parts = String(isoDate).split("-");
        if (parts.length !== 3) return isoDate;
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
    }

    function formatTimeShort(timeStr) {
        if (!timeStr) return "";
        return String(timeStr).slice(0, 5);
    }

    function escapeHtml(str) {
        if (str === null || str === undefined) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    function showToast(message, type = "success") {
        const container = document.getElementById("toast-container");
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => {
            toast.remove();
        }, 4000);
    }

    function openModal(modalId) {
        document.getElementById(modalId)?.classList.remove("hidden");
    }

    function closeModal(modalId) {
        document.getElementById(modalId)?.classList.add("hidden");
    }

    document.querySelectorAll("[data-close]").forEach((btn) => {
        btn.addEventListener("click", () => closeModal(btn.dataset.close));
    });

    // Navegação entre Telas
    function switchView(viewName) {
        state.currentView = viewName;
        document.querySelectorAll(".nav-item").forEach((btn) => {
            btn.classList.toggle("active", btn.dataset.view === viewName);
        });
        document.querySelectorAll(".view-section").forEach((sec) => {
            sec.classList.toggle("active", sec.id === `view-${viewName}`);
        });

        const meta = VIEW_METADATA[viewName];
        if (meta) {
            document.getElementById("view-title").textContent = meta.title;
            document.getElementById("view-subtitle").textContent = meta.subtitle;
        }

        if (viewName === "dashboard") loadDashboard();
        if (viewName === "agenda") loadAgendaDia();
        if (viewName === "agendamentos") loadAgendamentos();
        if (viewName === "clientes") loadClientes();
        if (viewName === "servicos") loadServicos();
        if (viewName === "relatorios") loadRelatorios();
    }

    document.querySelectorAll(".nav-item").forEach((btn) => {
        btn.addEventListener("click", () => switchView(btn.dataset.view));
    });

    document.querySelectorAll("[data-goto]").forEach((btn) => {
        btn.addEventListener("click", () => switchView(btn.dataset.goto));
    });

    // Carregar Contexto Inicial do Salão
    async function loadSalaoHeader() {
        const badgeEl = document.getElementById("salao-badge");
        const horariosUl = document.getElementById("dashboard-horarios-list");
        try {
            const info = await ApiClient.obterSalaoAtual();
            badgeEl.textContent = info.salao.nome;
            if (info.operador) {
                document.getElementById("operador-nome").textContent = info.operador.nome;
                document.getElementById("operador-cargo").textContent = info.operador.cargo;
            }

            if (!info.horarios_funcionamento || !info.horarios_funcionamento.length) {
                horariosUl.innerHTML = `<li class="text-muted">Nenhum horário de funcionamento cadastrado.</li>`;
                return;
            }

            horariosUl.innerHTML = info.horarios_funcionamento
                .map((h) => {
                    const intervalo = h.aberto
                        ? `${formatTimeShort(h.hora_abertura)} às ${formatTimeShort(h.hora_fechamento)}`
                        : "Fechado";
                    return `<li>
                        <span><strong>${escapeHtml(h.dia_nome)}</strong></span>
                        <span class="badge ${h.aberto ? "badge-ativo" : "badge-inativo"}">${intervalo}</span>
                    </li>`;
                })
                .join("");
        } catch (err) {
            badgeEl.textContent = "Erro ao carregar salão";
            document.getElementById("operador-nome").textContent = "Indisponível";
            horariosUl.innerHTML = `<li class="empty-row">Não foi possível carregar os horários (${escapeHtml(err.message)}).</li>`;
            showToast(err.message, "error");
        }
    }

    async function refreshSelectOptions() {
        const [clientes, servicos] = await Promise.all([
            ApiClient.listarClientes(),
            ApiClient.listarServicos(),
        ]);
        state.todosClientes = clientes;
        state.todosServicos = servicos;
        state.clientesAtivos = clientes.filter((c) => c.ativo);
        state.servicosAtivos = servicos.filter((s) => s.ativo);

        // Select de filtro de agendamentos (Cliente e Serviço)
        const filtroCli = document.getElementById("filtro-ag-cliente");
        const currentVal = filtroCli.value;
        filtroCli.innerHTML =
            `<option value="">Todos os clientes</option>` +
            clientes
                .map(
                    (c) =>
                        `<option value="${c.id}">${escapeHtml(c.nome)} (${escapeHtml(c.telefone)})</option>`
                )
                .join("");
        filtroCli.value = currentVal;

        const filtroSrv = document.getElementById("filtro-ag-servico");
        if (filtroSrv) {
            const currentSrvVal = filtroSrv.value;
            filtroSrv.innerHTML =
                `<option value="">Todos os serviços</option>` +
                servicos
                    .map(
                        (s) =>
                            `<option value="${s.id}">${escapeHtml(s.nome)} (${s.duracao_minutos} min)</option>`
                    )
                    .join("");
            filtroSrv.value = currentSrvVal;
        }

        // Selects do modal de novo agendamento e reagendamento
        const agCli = document.getElementById("ag-cliente");
        agCli.innerHTML = state.clientesAtivos
            .map(
                (c) =>
                    `<option value="${c.id}">${escapeHtml(c.nome)} — ${escapeHtml(c.telefone)}</option>`
            )
            .join("");

        const servicosOptionsHtml = state.servicosAtivos
            .map(
                (s) =>
                    `<option value="${s.id}">${escapeHtml(s.nome)} (${s.duracao_minutos} min — ${formatCurrency(s.preco)})</option>`
            )
            .join("");
        document.getElementById("ag-servico").innerHTML = servicosOptionsHtml;
        document.getElementById("reag-servico").innerHTML = servicosOptionsHtml;
    }

    // =========================================================================
    // 1. DASHBOARD
    // =========================================================================
    async function loadDashboard() {
        const tbody = document.getElementById("dashboard-agendamentos-tbody");
        try {
            const rel = await ApiClient.obterRelatorioResumo();
            const ind = rel.indicadores;

            document.getElementById("kpi-agendamentos-ativos").textContent =
                ind.agendamentos_ativos;
            document.getElementById("kpi-agendamentos-total").textContent =
                `${ind.total_agendamentos} registrados (${ind.taxa_cancelamento_percentual}% cancelados)`;

            document.getElementById("kpi-clientes-ativos").textContent =
                ind.clientes_ativos;
            document.getElementById("kpi-clientes-total").textContent =
                `${ind.total_clientes} cadastrados no salão`;

            document.getElementById("kpi-servicos-ativos").textContent =
                ind.servicos_ativos;
            document.getElementById("kpi-servicos-total").textContent =
                `${ind.total_servicos} serviços no catálogo`;

            document.getElementById("kpi-receita-prevista").textContent =
                formatCurrency(ind.faturamento_previsto);
            document.getElementById("kpi-receita-realizada").textContent =
                `Concluído: ${formatCurrency(ind.faturamento_realizado)}`;

            if (!rel.agendamentos_recentes.length) {
                tbody.innerHTML = `<tr><td colspan="5" class="empty-row">Nenhum agendamento cadastrado.</td></tr>`;
                return;
            }
            tbody.innerHTML = rel.agendamentos_recentes
                .map(
                    (a) => `<tr>
                        <td><strong>${formatDateBR(a.data)}</strong> às ${formatTimeShort(a.hora_inicio)}</td>
                        <td>${escapeHtml(a.cliente_nome)}</td>
                        <td>${escapeHtml(a.servico_nome)}</td>
                        <td>${escapeHtml(a.canal_origem)}</td>
                        <td><span class="badge badge-${a.status}">${a.status}</span></td>
                    </tr>`
                )
                .join("");
        } catch (err) {
            document.getElementById("kpi-agendamentos-ativos").textContent = "—";
            document.getElementById("kpi-agendamentos-total").textContent = "Indisponível";
            document.getElementById("kpi-clientes-ativos").textContent = "—";
            document.getElementById("kpi-clientes-total").textContent = "Indisponível";
            document.getElementById("kpi-servicos-ativos").textContent = "—";
            document.getElementById("kpi-servicos-total").textContent = "Indisponível";
            document.getElementById("kpi-receita-prevista").textContent = "—";
            document.getElementById("kpi-receita-realizada").textContent = "Falha ao consultar API";
            tbody.innerHTML = `<tr><td colspan="5" class="empty-row">Não foi possível carregar a movimentação da agenda (${escapeHtml(err.message)}).</td></tr>`;
            showToast(err.message, "error");
        }
    }

    // =========================================================================
    // 2. AGENDA POR DATA
    // =========================================================================
    const agendaDateInput = document.getElementById("agenda-date-input");
    agendaDateInput.value = state.agendaDate;

    function shiftAgendaDate(days) {
        const current = new Date(`${agendaDateInput.value}T12:00:00`);
        current.setDate(current.getDate() + days);
        state.agendaDate = current.toISOString().slice(0, 10);
        agendaDateInput.value = state.agendaDate;
        loadAgendaDia();
    }

    agendaDateInput.addEventListener("change", () => {
        state.agendaDate = agendaDateInput.value;
        loadAgendaDia();
    });
    document
        .getElementById("btn-agenda-prev")
        .addEventListener("click", () => shiftAgendaDate(-1));
    document
        .getElementById("btn-agenda-next")
        .addEventListener("click", () => shiftAgendaDate(1));
    document.getElementById("btn-agenda-today").addEventListener("click", () => {
        const today = new Date().toISOString().slice(0, 10);
        state.agendaDate = today;
        agendaDateInput.value = today;
        loadAgendaDia();
    });

    async function loadAgendaDia() {
        try {
            const agenda = await ApiClient.consultarAgendaDia(state.agendaDate);
            const banner = document.getElementById("agenda-expediente-banner");

            if (agenda.expediente && agenda.expediente.aberto) {
                banner.textContent = `${agenda.expediente.dia_nome}: Aberto das ${formatTimeShort(agenda.expediente.hora_abertura)} às ${formatTimeShort(agenda.expediente.hora_fechamento)}`;
            } else {
                const nomeDia = agenda.expediente ? agenda.expediente.dia_nome : "Dia selecionado";
                banner.textContent = `${nomeDia}: Salão Fechado`;
            }

            document.getElementById("agenda-kpi-ativos").textContent =
                agenda.resumo.ativos;
            document.getElementById("agenda-kpi-confirmados").textContent =
                `${agenda.resumo.confirmados} / ${agenda.resumo.concluidos}`;
            document.getElementById("agenda-kpi-cancelados").textContent =
                agenda.resumo.cancelados;
            document.getElementById("agenda-kpi-receita").textContent =
                formatCurrency(agenda.resumo.faturamento_previsto_dia);

            const tbody = document.getElementById("agenda-dia-tbody");
            if (!agenda.agendamentos.length) {
                tbody.innerHTML = `<tr><td colspan="7" class="empty-row">Nenhum agendamento para ${formatDateBR(state.agendaDate)}.</td></tr>`;
            } else {
                tbody.innerHTML = agenda.agendamentos
                    .map((a) => renderAgendamentoRow(a, true))
                    .join("");
            }

            const slotsGrid = document.getElementById("agenda-slots-grid");
            if (!agenda.grade_horarios.length) {
                slotsGrid.innerHTML = `<p class="text-muted">O salão não possui expediente aberto nesta data.</p>`;
            } else {
                slotsGrid.innerHTML = agenda.grade_horarios
                    .map((slot) => {
                        if (slot.disponivel) {
                            return `<div class="slot-item free" data-slot-time="${slot.horario}" title="Clique para agendar neste horário">
                                <span class="slot-time">${slot.horario}</span>
                                <span class="slot-meta">Disponível (+ Agendar)</span>
                            </div>`;
                        }
                        return `<div class="slot-item busy">
                            <span class="slot-time">${slot.horario}</span>
                            <span class="slot-meta">${escapeHtml(slot.cliente_nome)}</span>
                            <span class="slot-meta">${escapeHtml(slot.servico_nome)}</span>
                        </div>`;
                    })
                    .join("");

                slotsGrid.querySelectorAll(".slot-item.free").forEach((el) => {
                    el.addEventListener("click", () => {
                        openNovoAgendamentoModal(state.agendaDate, el.dataset.slotTime);
                    });
                });
            }
        } catch (err) {
            document.getElementById("agenda-expediente-banner").textContent =
                "Falha ao consultar expediente";
            document.getElementById("agenda-kpi-ativos").textContent = "—";
            document.getElementById("agenda-kpi-confirmados").textContent = "—";
            document.getElementById("agenda-kpi-cancelados").textContent = "—";
            document.getElementById("agenda-kpi-receita").textContent = "—";
            document.getElementById("agenda-dia-tbody").innerHTML =
                `<tr><td colspan="7" class="empty-row">Erro ao carregar a agenda (${escapeHtml(err.message)}).</td></tr>`;
            document.getElementById("agenda-slots-grid").innerHTML =
                `<p class="text-muted">Não foi possível carregar a grade de horários.</p>`;
            showToast(err.message, "error");
        }
    }

    // =========================================================================
    // 3. AGENDAMENTOS
    // =========================================================================
    function renderAgendamentoRow(a, compact = false) {
        const canModify = a.status !== "CANCELADO" && a.status !== "CONCLUIDO";
        const actionsHtml = canModify
            ? `<div class="actions-cell">
                ${
                    a.status === "AGENDADO"
                        ? `<button class="btn btn-outline btn-sm" data-action="confirmar" data-id="${a.id}">Confirmar</button>`
                        : ""
                }
                <button class="btn btn-success btn-sm" data-action="concluir" data-id="${a.id}">Concluir</button>
                <button class="btn btn-outline btn-sm" data-action="reagendar" data-id="${a.id}">Reagendar</button>
                <button class="btn btn-danger btn-sm" data-action="cancelar" data-id="${a.id}">Cancelar</button>
               </div>`
            : `<span class="text-muted">Finalizado</span>`;

        if (compact) {
            return `<tr>
                <td><strong>${formatTimeShort(a.hora_inicio)} - ${formatTimeShort(a.hora_fim)}</strong></td>
                <td>${escapeHtml(a.cliente_nome)}<br/><small class="text-muted">${escapeHtml(a.cliente_telefone)}</small></td>
                <td>${escapeHtml(a.servico_nome)} (${a.servico_duracao_minutos}m)</td>
                <td>${escapeHtml(a.canal_origem)}</td>
                <td>${formatCurrency(a.valor_cobrado)}</td>
                <td><span class="badge badge-${a.status}">${a.status}</span></td>
                <td>${actionsHtml}</td>
            </tr>`;
        }

        return `<tr>
            <td>#${a.id}</td>
            <td><strong>${formatDateBR(a.data)}</strong></td>
            <td>${formatTimeShort(a.hora_inicio)} às ${formatTimeShort(a.hora_fim)}</td>
            <td>${escapeHtml(a.cliente_nome)}<br/><small class="text-muted">${escapeHtml(a.cliente_telefone)}</small></td>
            <td>${escapeHtml(a.servico_nome)} (${a.servico_duracao_minutos} min)</td>
            <td>${escapeHtml(a.canal_origem)}</td>
            <td>${formatCurrency(a.valor_cobrado)}</td>
            <td><span class="badge badge-${a.status}">${a.status}</span></td>
            <td>${actionsHtml}</td>
        </tr>`;
    }

    async function loadAgendamentos() {
        try {
            await refreshSelectOptions();
            const filtros = {
                data: document.getElementById("filtro-ag-data").value,
                cliente_id: document.getElementById("filtro-ag-cliente").value,
                servico_id: document.getElementById("filtro-ag-servico")?.value || "",
                status: document.getElementById("filtro-ag-status").value,
            };
            const lista = await ApiClient.listarAgendamentos(filtros);
            const tbody = document.getElementById("agendamentos-tbody");
            if (!lista.length) {
                tbody.innerHTML = `<tr><td colspan="9" class="empty-row">Nenhum agendamento encontrado para os filtros informados.</td></tr>`;
                return;
            }
            tbody.innerHTML = lista.map((a) => renderAgendamentoRow(a, false)).join("");
        } catch (err) {
            document.getElementById("agendamentos-tbody").innerHTML =
                `<tr><td colspan="9" class="empty-row">Erro ao carregar agendamentos (${escapeHtml(err.message)}).</td></tr>`;
            showToast(err.message, "error");
        }
    }

    document
        .getElementById("btn-filtrar-agendamentos")
        .addEventListener("click", loadAgendamentos);
    document.getElementById("btn-limpar-agendamentos").addEventListener("click", () => {
        document.getElementById("filtro-ag-data").value = "";
        document.getElementById("filtro-ag-cliente").value = "";
        const filtroSrv = document.getElementById("filtro-ag-servico");
        if (filtroSrv) filtroSrv.value = "";
        document.getElementById("filtro-ag-status").value = "";
        loadAgendamentos();
    });

    async function openNovoAgendamentoModal(defaultDate = null, defaultTime = "09:00") {
        await refreshSelectOptions();
        if (!state.clientesAtivos.length) {
            showToast("Cadastre ou ative pelo menos um cliente antes de agendar.", "error");
            return;
        }
        if (!state.servicosAtivos.length) {
            showToast("Cadastre ou ative pelo menos um serviço antes de agendar.", "error");
            return;
        }
        document.getElementById("ag-data").value = defaultDate || state.agendaDate;
        document.getElementById("ag-hora").value = defaultTime;
        document.getElementById("ag-observacoes").value = "";
        openModal("modal-agendamento");
    }

    document
        .getElementById("btn-quick-agendamento")
        .addEventListener("click", () => openNovoAgendamentoModal());
    document
        .getElementById("btn-novo-agendamento-view")
        .addEventListener("click", () => openNovoAgendamentoModal());

    document
        .getElementById("form-agendamento")
        .addEventListener("submit", async (e) => {
            e.preventDefault();
            try {
                const payload = {
                    cliente_id: Number(document.getElementById("ag-cliente").value),
                    servico_id: Number(document.getElementById("ag-servico").value),
                    data: document.getElementById("ag-data").value,
                    hora_inicio: document.getElementById("ag-hora").value,
                    canal_origem: document.getElementById("ag-canal").value,
                    observacoes:
                        document.getElementById("ag-observacoes").value.trim() || null,
                };
                await ApiClient.criarAgendamento(payload);
                closeModal("modal-agendamento");
                showToast("Agendamento criado com sucesso!");
                switchView(state.currentView);
            } catch (err) {
                showToast(err.message, "error");
            }
        });

    // Delegação de eventos para botões de ação de agendamentos (Confirmar, Concluir, Reagendar, Cancelar)
    document.body.addEventListener("click", async (e) => {
        const btn = e.target.closest("button[data-action]");
        if (!btn) return;
        const action = btn.dataset.action;
        const id = Number(btn.dataset.id);

        try {
            if (action === "confirmar") {
                await ApiClient.atualizarStatusAgendamento(id, "CONFIRMADO");
                showToast(`Agendamento #${id} confirmado!`);
                switchView(state.currentView);
            } else if (action === "concluir") {
                await ApiClient.atualizarStatusAgendamento(id, "CONCLUIDO");
                showToast(`Atendimento #${id} marcado como concluído!`);
                switchView(state.currentView);
            } else if (action === "cancelar") {
                const motivo = window.prompt(
                    `Confirmar cancelamento do agendamento #${id}?\nInforme o motivo (ou clique em Cancelar para abortar):`,
                    "Cancelado pela recepção"
                );
                if (motivo === null) return;
                await ApiClient.cancelarAgendamento(id, motivo.trim());
                showToast(`Agendamento #${id} cancelado e horário liberado.`);
                switchView(state.currentView);
            } else if (action === "reagendar") {
                await refreshSelectOptions();
                const ag = await ApiClient.obterAgendamento(id);
                if (!ag) return;
                const reagSelect = document.getElementById("reag-servico");
                if (!state.servicosAtivos.some((s) => s.id === ag.servico_id)) {
                    reagSelect.insertAdjacentHTML(
                        "beforeend",
                        `<option value="${ag.servico_id}">${escapeHtml(ag.servico_nome)} (${ag.servico_duracao_minutos} min — atual)</option>`
                    );
                }
                document.getElementById("reag-id").value = ag.id;
                document.getElementById("reag-resumo").textContent =
                    `Cliente: ${ag.cliente_nome} | Atual: ${formatDateBR(ag.data)} às ${formatTimeShort(ag.hora_inicio)}`;
                reagSelect.value = ag.servico_id;
                document.getElementById("reag-data").value = ag.data;
                document.getElementById("reag-hora").value = formatTimeShort(ag.hora_inicio);
                document.getElementById("reag-observacoes").value = ag.observacoes || "";
                openModal("modal-reagendar");
            }
        } catch (err) {
            showToast(err.message, "error");
        }
    });

    document
        .getElementById("form-reagendar")
        .addEventListener("submit", async (e) => {
            e.preventDefault();
            try {
                const id = Number(document.getElementById("reag-id").value);
                const payload = {
                    servico_id: Number(document.getElementById("reag-servico").value),
                    data: document.getElementById("reag-data").value,
                    hora_inicio: document.getElementById("reag-hora").value,
                    observacoes:
                        document.getElementById("reag-observacoes").value.trim() || null,
                };
                await ApiClient.reagendarAgendamento(id, payload);
                closeModal("modal-reagendar");
                showToast(`Agendamento #${id} reagendado com sucesso!`);
                switchView(state.currentView);
            } catch (err) {
                showToast(err.message, "error");
            }
        });

    // =========================================================================
    // 4. CLIENTES
    // =========================================================================
    async function loadClientes() {
        try {
            const busca = document.getElementById("filtro-cliente-busca").value;
            const apenas_ativos = document.getElementById("filtro-cliente-status").value;
            const clientes = await ApiClient.listarClientes({ busca, apenas_ativos });
            state.todosClientes = clientes;

            const tbody = document.getElementById("clientes-tbody");
            if (!clientes.length) {
                tbody.innerHTML = `<tr><td colspan="7" class="empty-row">Nenhum cliente encontrado.</td></tr>`;
                return;
            }
            tbody.innerHTML = clientes
                .map(
                    (c) => `<tr>
                        <td>#${c.id}</td>
                        <td><strong>${escapeHtml(c.nome)}</strong></td>
                        <td>${escapeHtml(c.telefone)}</td>
                        <td>${escapeHtml(c.email || "—")}</td>
                        <td>${escapeHtml(c.observacoes || "—")}</td>
                        <td><span class="badge ${c.ativo ? "badge-ativo" : "badge-inativo"}">${c.ativo ? "Ativo" : "Inativo"}</span></td>
                        <td>
                            <div class="actions-cell">
                                <button class="btn btn-outline btn-sm" data-cli-action="historico" data-id="${c.id}">Histórico</button>
                                <button class="btn btn-outline btn-sm" data-cli-action="editar" data-id="${c.id}">Editar</button>
                                ${
                                    c.ativo
                                        ? `<button class="btn btn-danger btn-sm" data-cli-action="inativar" data-id="${c.id}">Inativar</button>`
                                        : `<button class="btn btn-success btn-sm" data-cli-action="reativar" data-id="${c.id}">Reativar</button>`
                                }
                            </div>
                        </td>
                    </tr>`
                )
                .join("");
        } catch (err) {
            document.getElementById("clientes-tbody").innerHTML =
                `<tr><td colspan="7" class="empty-row">Erro ao carregar clientes (${escapeHtml(err.message)}).</td></tr>`;
            showToast(err.message, "error");
        }
    }

    document
        .getElementById("btn-buscar-clientes")
        .addEventListener("click", loadClientes);

    document.getElementById("btn-novo-cliente").addEventListener("click", () => {
        document.getElementById("modal-cliente-titulo").textContent = "Cadastrar Novo Cliente";
        document.getElementById("cliente-id").value = "";
        document.getElementById("cliente-nome").value = "";
        document.getElementById("cliente-telefone").value = "";
        document.getElementById("cliente-email").value = "";
        document.getElementById("cliente-observacoes").value = "";
        openModal("modal-cliente");
    });

    document
        .getElementById("form-cliente")
        .addEventListener("submit", async (e) => {
            e.preventDefault();
            try {
                const id = document.getElementById("cliente-id").value;
                const payload = {
                    nome: document.getElementById("cliente-nome").value.trim(),
                    telefone: document.getElementById("cliente-telefone").value.trim(),
                    email: document.getElementById("cliente-email").value.trim() || null,
                    observacoes:
                        document.getElementById("cliente-observacoes").value.trim() || null,
                };
                if (id) {
                    await ApiClient.editarCliente(Number(id), payload);
                    showToast("Dados do cliente atualizados!");
                } else {
                    await ApiClient.criarCliente(payload);
                    showToast("Cliente cadastrado com sucesso!");
                }
                closeModal("modal-cliente");
                loadClientes();
            } catch (err) {
                showToast(err.message, "error");
            }
        });

    document.getElementById("clientes-tbody").addEventListener("click", async (e) => {
        const btn = e.target.closest("button[data-cli-action]");
        if (!btn) return;
        const action = btn.dataset.cliAction;
        const id = Number(btn.dataset.id);

        try {
            if (action === "editar") {
                const c = await ApiClient.obterCliente(id);
                document.getElementById("modal-cliente-titulo").textContent = `Editar Cliente #${c.id}`;
                document.getElementById("cliente-id").value = c.id;
                document.getElementById("cliente-nome").value = c.nome;
                document.getElementById("cliente-telefone").value = c.telefone;
                document.getElementById("cliente-email").value = c.email || "";
                document.getElementById("cliente-observacoes").value = c.observacoes || "";
                openModal("modal-cliente");
            } else if (action === "inativar") {
                await ApiClient.inativarCliente(id);
                showToast("Cliente inativado com sucesso.");
                loadClientes();
            } else if (action === "reativar") {
                await ApiClient.reativarCliente(id);
                showToast("Cliente reativado com sucesso.");
                loadClientes();
            } else if (action === "historico") {
                const hist = await ApiClient.historicoCliente(id);
                document.getElementById("modal-historico-titulo").textContent =
                    `Histórico de Agendamentos — ${hist.cliente.nome}`;
                document.getElementById("modal-historico-subtitulo").textContent =
                    `Telefone: ${hist.cliente.telefone} | Total de registros: ${hist.total_agendamentos}`;
                const tbody = document.getElementById("historico-cliente-tbody");
                if (!hist.agendamentos.length) {
                    tbody.innerHTML = `<tr><td colspan="7" class="empty-row">Este cliente ainda não possui agendamentos registrados.</td></tr>`;
                } else {
                    tbody.innerHTML = hist.agendamentos
                        .map(
                            (a) => `<tr>
                                <td>${formatDateBR(a.data)}</td>
                                <td>${formatTimeShort(a.hora_inicio)} - ${formatTimeShort(a.hora_fim)}</td>
                                <td>${escapeHtml(a.servico_nome)}</td>
                                <td>${escapeHtml(a.canal_origem)}</td>
                                <td>${formatCurrency(a.valor_cobrado)}</td>
                                <td><span class="badge badge-${a.status}">${a.status}</span></td>
                                <td>${escapeHtml(a.observacoes || "—")}</td>
                            </tr>`
                        )
                        .join("");
                }
                openModal("modal-historico-cliente");
            }
        } catch (err) {
            showToast(err.message, "error");
        }
    });

    // =========================================================================
    // 5. SERVIÇOS
    // =========================================================================
    async function loadServicos() {
        try {
            const busca = document.getElementById("filtro-servico-busca").value;
            const apenas_ativos = document.getElementById("filtro-servico-status").value;
            const servicos = await ApiClient.listarServicos({ busca, apenas_ativos });
            state.todosServicos = servicos;

            const tbody = document.getElementById("servicos-tbody");
            if (!servicos.length) {
                tbody.innerHTML = `<tr><td colspan="7" class="empty-row">Nenhum serviço encontrado.</td></tr>`;
                return;
            }
            tbody.innerHTML = servicos
                .map(
                    (s) => `<tr>
                        <td>#${s.id}</td>
                        <td><strong>${escapeHtml(s.nome)}</strong></td>
                        <td>${escapeHtml(s.descricao || "—")}</td>
                        <td>${s.duracao_minutos} min</td>
                        <td><strong>${formatCurrency(s.preco)}</strong></td>
                        <td><span class="badge ${s.ativo ? "badge-ativo" : "badge-inativo"}">${s.ativo ? "Ativo" : "Inativo"}</span></td>
                        <td>
                            <div class="actions-cell">
                                <button class="btn btn-outline btn-sm" data-srv-action="editar" data-id="${s.id}">Editar</button>
                                ${
                                    s.ativo
                                        ? `<button class="btn btn-danger btn-sm" data-srv-action="inativar" data-id="${s.id}">Inativar</button>`
                                        : `<button class="btn btn-success btn-sm" data-srv-action="reativar" data-id="${s.id}">Reativar</button>`
                                }
                            </div>
                        </td>
                    </tr>`
                )
                .join("");
        } catch (err) {
            document.getElementById("servicos-tbody").innerHTML =
                `<tr><td colspan="7" class="empty-row">Erro ao carregar serviços (${escapeHtml(err.message)}).</td></tr>`;
            showToast(err.message, "error");
        }
    }

    document
        .getElementById("btn-buscar-servicos")
        .addEventListener("click", loadServicos);

    document.getElementById("btn-novo-servico").addEventListener("click", () => {
        document.getElementById("modal-servico-titulo").textContent = "Cadastrar Novo Serviço";
        document.getElementById("servico-id").value = "";
        document.getElementById("servico-nome").value = "";
        document.getElementById("servico-duracao").value = "60";
        document.getElementById("servico-preco").value = "";
        document.getElementById("servico-descricao").value = "";
        openModal("modal-servico");
    });

    document
        .getElementById("form-servico")
        .addEventListener("submit", async (e) => {
            e.preventDefault();
            try {
                const id = document.getElementById("servico-id").value;
                const payload = {
                    nome: document.getElementById("servico-nome").value.trim(),
                    duracao_minutos: Number(document.getElementById("servico-duracao").value),
                    preco: Number(document.getElementById("servico-preco").value),
                    descricao:
                        document.getElementById("servico-descricao").value.trim() || null,
                };
                if (id) {
                    await ApiClient.editarServico(Number(id), payload);
                    showToast("Serviço atualizado com sucesso!");
                } else {
                    await ApiClient.criarServico(payload);
                    showToast("Serviço cadastrado no catálogo!");
                }
                closeModal("modal-servico");
                loadServicos();
            } catch (err) {
                showToast(err.message, "error");
            }
        });

    document.getElementById("servicos-tbody").addEventListener("click", async (e) => {
        const btn = e.target.closest("button[data-srv-action]");
        if (!btn) return;
        const action = btn.dataset.srvAction;
        const id = Number(btn.dataset.id);

        try {
            if (action === "editar") {
                const s = await ApiClient.obterServico(id);
                document.getElementById("modal-servico-titulo").textContent = `Editar Serviço #${s.id}`;
                document.getElementById("servico-id").value = s.id;
                document.getElementById("servico-nome").value = s.nome;
                document.getElementById("servico-duracao").value = s.duracao_minutos;
                document.getElementById("servico-preco").value = s.preco;
                document.getElementById("servico-descricao").value = s.descricao || "";
                openModal("modal-servico");
            } else if (action === "inativar") {
                await ApiClient.inativarServico(id);
                showToast("Serviço inativado.");
                loadServicos();
            } else if (action === "reativar") {
                await ApiClient.reativarServico(id);
                showToast("Serviço reativado.");
                loadServicos();
            }
        } catch (err) {
            showToast(err.message, "error");
        }
    });

    // =========================================================================
    // 6. RELATÓRIOS
    // =========================================================================
    async function loadRelatorios() {
        try {
            const data_inicio = document.getElementById("rel-data-inicio").value;
            const data_fim = document.getElementById("rel-data-fim").value;
            const rel = await ApiClient.obterRelatorioResumo({ data_inicio, data_fim });
            const ind = rel.indicadores;

            document.getElementById("rel-total-agendamentos").textContent =
                ind.total_agendamentos;
            document.getElementById("rel-taxa-cancelamento").textContent =
                `Taxa de cancelamento: ${ind.taxa_cancelamento_percentual}%`;

            document.getElementById("rel-concluidos-confirmados").textContent =
                `${rel.por_status.CONCLUIDO} / ${rel.por_status.CONFIRMADO}`;
            document.getElementById("rel-pendentes").textContent =
                `${rel.por_status.AGENDADO} com status AGENDADO`;

            document.getElementById("rel-faturamento-realizado").textContent =
                formatCurrency(ind.faturamento_realizado);
            document.getElementById("rel-faturamento-previsto").textContent =
                formatCurrency(ind.faturamento_previsto);

            const srvTbody = document.getElementById("rel-servicos-tbody");
            if (!rel.desempenho_servicos.length) {
                srvTbody.innerHTML = `<tr><td colspan="5" class="empty-row">Sem movimentação de serviços no período.</td></tr>`;
            } else {
                srvTbody.innerHTML = rel.desempenho_servicos
                    .map(
                        (s) => `<tr>
                            <td><strong>${escapeHtml(s.servico_nome)}</strong></td>
                            <td>${s.duracao_minutos} min</td>
                            <td>${s.ativos_ou_concluidos}</td>
                            <td>${s.cancelados}</td>
                            <td><strong>${formatCurrency(s.receita_gerada)}</strong></td>
                        </tr>`
                    )
                    .join("");
            }

            const movTbody = document.getElementById("rel-movimentacao-tbody");
            if (!rel.movimentacao_diaria.length) {
                movTbody.innerHTML = `<tr><td colspan="6" class="empty-row">Sem agendamentos no período.</td></tr>`;
            } else {
                movTbody.innerHTML = rel.movimentacao_diaria
                    .map(
                        (m) => `<tr>
                            <td><strong>${formatDateBR(m.data)}</strong></td>
                            <td>${m.total}</td>
                            <td>${m.ativos}</td>
                            <td>${m.concluidos}</td>
                            <td>${m.cancelados}</td>
                            <td>${formatCurrency(m.receita_prevista)}</td>
                        </tr>`
                    )
                    .join("");
            }

            const pillsBox = document.getElementById("rel-canais-status-box");
            const statusEntries = Object.entries(rel.por_status).map(
                ([k, v]) => `<div class="stat-pill">Status <strong>${k}</strong>: ${v}</div>`
            );
            const canalEntries = Object.entries(rel.por_canal_origem).map(
                ([k, v]) => `<div class="stat-pill">Canal <strong>${escapeHtml(k)}</strong>: ${v}</div>`
            );
            pillsBox.innerHTML = [...statusEntries, ...canalEntries].join("");
        } catch (err) {
            document.getElementById("rel-total-agendamentos").textContent = "—";
            document.getElementById("rel-taxa-cancelamento").textContent = "Indisponível";
            document.getElementById("rel-concluidos-confirmados").textContent = "—";
            document.getElementById("rel-pendentes").textContent = "Indisponível";
            document.getElementById("rel-faturamento-realizado").textContent = "—";
            document.getElementById("rel-faturamento-previsto").textContent = "—";
            document.getElementById("rel-servicos-tbody").innerHTML =
                `<tr><td colspan="5" class="empty-row">Erro ao carregar relatório (${escapeHtml(err.message)}).</td></tr>`;
            document.getElementById("rel-movimentacao-tbody").innerHTML =
                `<tr><td colspan="6" class="empty-row">Erro ao carregar movimentação (${escapeHtml(err.message)}).</td></tr>`;
            document.getElementById("rel-canais-status-box").innerHTML = "";
            showToast(err.message, "error");
        }
    }

    document
        .getElementById("btn-gerar-relatorio")
        .addEventListener("click", loadRelatorios);
    document.getElementById("btn-limpar-relatorio").addEventListener("click", () => {
        document.getElementById("rel-data-inicio").value = "";
        document.getElementById("rel-data-fim").value = "";
        loadRelatorios();
    });

    // Inicialização
    loadSalaoHeader();
    loadDashboard();
});
