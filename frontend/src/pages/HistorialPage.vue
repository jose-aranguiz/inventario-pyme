<template>
  <q-page padding>
    <div class="q-mb-md">
      <span class="text-h4">Historial de Movimientos</span>
    </div>

    <q-table
      title="Registro de Entradas y Salidas"
      :rows="movimientos"
      :columns="columns"
      row-key="id"
      :loading="loading"
      :pagination="{ rowsPerPage: 15, sortBy: 'fecha_hora', descending: true }"
    >
      <template v-slot:body-cell-fecha="props">
        <q-td :props="props">
          {{ formatearFecha(props.row.fecha_hora) }}
        </q-td>
      </template>

      <template v-slot:body-cell-tipo="props">
        <q-td :props="props">
          <q-chip
            :color="props.row.tipo === 'ENTRADA' ? 'positive' : 'negative'"
            text-color="white"
            dense
            square
          >
            {{ props.row.tipo }}
          </q-chip>
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'boot/axios'
import { useQuasar, date } from 'quasar'

const $q = useQuasar()
const loading = ref(true)
const movimientos = ref([])

const columns = [
  { name: 'fecha', label: 'Fecha y Hora', field: 'fecha_hora', sortable: true, align: 'left' },
  { name: 'producto', label: 'Producto', field: row => row.producto?.nombre || 'Producto eliminado', align: 'left', sortable: true },
  { name: 'tipo', label: 'Tipo', field: 'tipo', align: 'center', sortable: true },
  { name: 'cantidad', label: 'Cantidad', field: 'cantidad', sortable: true },
  { name: 'motivo', label: 'Motivo / Observación', field: 'motivo', align: 'left' }
]

const cargarMovimientos = async () => {
  try {
    loading.value = true
    const response = await api.get('/movimientos/')
    movimientos.value = response.data
  } catch {
    $q.notify({ color: 'negative', message: 'Error cargando el historial', icon: 'error' })
  } finally {
    loading.value = false
  }
}

// Función auxiliar para mostrar la fecha en formato local legible
const formatearFecha = (fechaISO) => {
  return date.formatDate(fechaISO, 'DD/MM/YYYY HH:mm')
}

onMounted(() => {
  cargarMovimientos()
})
</script>