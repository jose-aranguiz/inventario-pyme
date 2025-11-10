<template>
  <q-page padding>
    <div class="row q-mb-md items-center justify-between">
      <span class="text-h4">Inventario</span>
      <q-btn color="primary" label="Nuevo Producto" icon="add" @click="abrirDialogo" />
    </div>

    <q-table
      title="Listado de Productos"
      :rows="productos"
      :columns="columns"
      row-key="id"
      :loading="loading"
    />

    <q-dialog v-model="dialogoVisible">
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">Nuevo Producto</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="guardarProducto" class="q-gutter-md">
            <q-input
              filled
              v-model="nuevoProducto.nombre"
              label="Nombre del producto *"
              lazy-rules
              :rules="[ val => val && val.length > 0 || 'El nombre es obligatorio']"
            />
            <q-input
              filled
              v-model="nuevoProducto.codigo_sku"
              label="Código SKU (Opcional)"
            />
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  filled
                  type="number"
                  v-model.number="nuevoProducto.precio_costo"
                  label="Precio Costo"
                  prefix="$"
                />
              </div>
              <div class="col-6">
                <q-input
                  filled
                  type="number"
                  v-model.number="nuevoProducto.precio_venta"
                  label="Precio Venta"
                  prefix="$"
                />
              </div>
            </div>
             <q-input
              filled
              type="number"
              v-model.number="nuevoProducto.stock_minimo"
              label="Stock Mínimo para Alerta"
            />

            <div align="right">
              <q-btn flat label="Cancelar" color="primary" v-close-popup />
              <q-btn label="Guardar" type="submit" color="primary" :loading="guardando" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { api } from 'boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const loading = ref(true)
const guardando = ref(false)
const productos = ref([])
const dialogoVisible = ref(false)

// Datos del formulario
const nuevoProducto = reactive({
  nombre: '',
  codigo_sku: '',
  precio_costo: 0,
  precio_venta: 0,
  stock_minimo: 5
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'nombre', label: 'Nombre', field: 'nombre', sortable: true, align: 'left' },
  { name: 'sku', label: 'SKU', field: 'codigo_sku', align: 'left' },
  { name: 'precio_venta', label: 'Precio Venta', field: 'precio_venta', format: val => `$ ${val}` },
  { name: 'stock', label: 'Stock Actual', field: 'stock_actual', sortable: true }
]

const cargarProductos = async () => {
  try {
    loading.value = true
    const response = await api.get('/productos/')
    productos.value = response.data
  } catch {
  $q.notify({ color: 'negative', message: 'Error cargando productos', icon: 'error' })
  } finally {
    loading.value = false
  }
}

const abrirDialogo = () => {
  // Reseteamos el formulario antes de abrirlo
  nuevoProducto.nombre = ''
  nuevoProducto.codigo_sku = ''
  nuevoProducto.precio_costo = 0
  nuevoProducto.precio_venta = 0
  nuevoProducto.stock_minimo = 5
  dialogoVisible.value = true
}

const guardarProducto = async () => {
  try {
    guardando.value = true
    // Enviamos los datos al backend
    await api.post('/productos/', nuevoProducto)
    
    // Si todo sale bien:
    $q.notify({ color: 'positive', message: 'Producto creado correctamente', icon: 'check' })
    dialogoVisible.value = false // Cerramos el diálogo
    cargarProductos() // Recargamos la tabla para ver el nuevo producto
  } catch (error) {
    // Si el backend nos devuelve un error (ej. SKU duplicado), lo mostramos
    const mensajeError = error.response?.data?.detail || 'Error al guardar el producto'
    $q.notify({ color: 'negative', message: mensajeError, icon: 'report_problem' })
  } finally {
    guardando.value = false
  }
}

onMounted(() => {
  cargarProductos()
})
</script>