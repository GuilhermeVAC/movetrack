document.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch('/api/movimentacoes');
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        const data = await response.json();

        const tbody = document.getElementById('movimentacoes-tbody');
        if (!tbody) {
            console.error('Elemento "movimentacoes-tbody" não encontrado.');
            return;
        }

        // Limpa o conteúdo existente (caso a tabela seja atualizada)
        tbody.innerHTML = '';

        // Verifica se os dados retornados são um array
        if (Array.isArray(data)) {
            data.forEach(mov => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${mov.id}</td>
                    <td>${mov.posicao}</td>
                    <td>${mov.estado === 1 ? 'Movimentado' : 'Parado'}</td>
                    <td>${mov.timestamp}</td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            console.error('Dados inesperados:', data);
        }
    } catch (error) {
        console.error('Erro ao buscar movimentações:', error);
    }
});
