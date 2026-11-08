/**
 * Camada de Comunicação HTTP do Frontend com a API FastAPI do BeautySchedule.
 */

const ApiClient = (() => {
    async function request(path, options = {}) {
        const config = {
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {}),
            },
            ...options,
        };

        const response = await fetch(path, config);
        let data = null;
        try {
            data = await response.json();
        } catch (_err) {
            data = null;
        }

        if (!response.ok) {
            let errorMessage = "Ocorreu um erro ao processar a solicitação.";
            if (data) {
                if (typeof data.mensagem === "string") {
                    errorMessage = data.mensagem;
                } else if (typeof data.detail === "string") {
                    errorMessage = data.detail;
                } else if (Array.isArray(data.detail) && data.detail.length > 0) {
                    errorMessage = data.detail
                        .map((item) => item.msg || JSON.stringify(item))
                        .join(" | ");
                }
            }
            throw new Error(errorMessage);
        }

        return data;
    }

    function buildQuery(params = {}) {
        const searchParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== "") {
                searchParams.append(key, String(value));
            }
        });
        const qs = searchParams.toString();
        return qs ? `?${qs}` : "";
    }

    return {
        // Salão e Expediente
        obterSalaoAtual: () => request("/api/salao"),

        // Clientes
        listarClientes: (filtros = {}) =>
            request(`/api/clientes${buildQuery(filtros)}`),
        obterCliente: (id) => request(`/api/clientes/${id}`),
        historicoCliente: (id) => request(`/api/clientes/${id}/agendamentos`),
        criarCliente: (payload) =>
            request("/api/clientes", {
                method: "POST",
                body: JSON.stringify(payload),
            }),
        editarCliente: (id, payload) =>
            request(`/api/clientes/${id}`, {
                method: "PUT",
                body: JSON.stringify(payload),
            }),
        inativarCliente: (id) =>
            request(`/api/clientes/${id}/inativar`, { method: "PATCH" }),
        reativarCliente: (id) =>
            request(`/api/clientes/${id}/reativar`, { method: "PATCH" }),

        // Serviços
        listarServicos: (filtros = {}) =>
            request(`/api/servicos${buildQuery(filtros)}`),
        obterServico: (id) => request(`/api/servicos/${id}`),
        criarServico: (payload) =>
            request("/api/servicos", {
                method: "POST",
                body: JSON.stringify(payload),
            }),
        editarServico: (id, payload) =>
            request(`/api/servicos/${id}`, {
                method: "PUT",
                body: JSON.stringify(payload),
            }),
        inativarServico: (id) =>
            request(`/api/servicos/${id}/inativar`, { method: "PATCH" }),
        reativarServico: (id) =>
            request(`/api/servicos/${id}/reativar`, { method: "PATCH" }),

        // Agendamentos e Agenda
        listarAgendamentos: (filtros = {}) =>
            request(`/api/agendamentos${buildQuery(filtros)}`),
        criarAgendamento: (payload) =>
            request("/api/agendamentos", {
                method: "POST",
                body: JSON.stringify(payload),
            }),
        reagendarAgendamento: (id, payload) =>
            request(`/api/agendamentos/${id}/reagendar`, {
                method: "PUT",
                body: JSON.stringify(payload),
            }),
        cancelarAgendamento: (id, motivo = "") =>
            request(`/api/agendamentos/${id}/cancelar${buildQuery({ motivo })}`, {
                method: "PATCH",
            }),
        atualizarStatusAgendamento: (id, status, observacoes = null) =>
            request(`/api/agendamentos/${id}/status`, {
                method: "PATCH",
                body: JSON.stringify({ status, observacoes }),
            }),
        consultarAgendaDia: (data) =>
            request(`/api/agenda${buildQuery({ data })}`),

        // Relatórios
        obterRelatorioResumo: (filtros = {}) =>
            request(`/api/relatorios/resumo${buildQuery(filtros)}`),
    };
})();
