<template>
  <q-page padding>
    <div class="row q-mb-md items-center justify-between">
      <span class="text-h4">Inventario</span>
      <q-btn color="primary" label="Nuevo Producto" icon="add" @click="abrirDialogoCrear" />
    </div>

    <q-table
      title="Listado de Productos"
      :rows="productos"
      :columns="columns"
      row-key="id"
      :loading="loading"
    >
      <template v-slot:body-cell-stock="props">
        <q-td :props="props">
          <q-chip
            :color="props.row.stock_actual < props.row.stock_minimo ? 'negative' : 'positive'"
            text-color="white"
            dense
          >
            {{ props.row.stock_actual }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-acciones="props">
        <q-td :props="props" auto-width>
          <div class="row q-gutter-xs no-wrap">
            <q-btn round dense color="negative" icon="remove" size="sm" @click="abrirDialogoMovimiento('SALIDA', props.row)">
              <q-tooltip>Registrar Salida</q-tooltip>
            </q-btn>
            <q-btn round dense color="positive" icon="add" size="sm" @click="abrirDialogoMovimiento('ENTRADA', props.row)">
              <q-tooltip>Registrar Entrada</q-tooltip>
            </q-btn>
            
            <q-separator vertical class="q-mx-sm" />
            
            <q-btn round dense color="primary" icon="edit" size="sm" @click="abrirDialogoEditar(props.row)">
              <q-tooltip>Editar Producto</q-tooltip>
            </q-btn>
            <q-btn round dense color="grey-8" icon="delete" size="sm" @click="confirmarEliminar(props.row)">
              <q-tooltip>Eliminar Producto</q-tooltip>
            </q-btn>
          </div>
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="dialogoProductoVisible">
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">{{ modoEdicion ? 'Editar Producto' : 'Nuevo Producto' }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="guardarProducto" class="q-gutter-md">
            <q-input
              filled
              v-model="formProducto.nombre"
              label="Nombre del producto *"
              lazy-rules
              :rules="[val => (val && val.length > 0) || 'El nombre es obligatorio']"
            />
            <q-input filled v-model="formProducto.codigo_sku" label="Código SKU (Opcional)" />
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input filled type="number" v-model.number="formProducto.precio_costo" label="Precio Costo" prefix="$" />
              </div>
              <div class="col-6">
                <q-input filled type="number" v-model.number="formProducto.precio_venta" label="Precio Venta" prefix="$" />
              </div>
            </div>
            <q-input filled type="number" v-model.number="formProducto.stock_minimo" label="Stock Mínimo para Alerta" />

            <div align="right">
              <q-btn flat label="Cancelar" color="primary" v-close-popup />
              <q-btn :label="modoEdicion ? 'Actualizar' : 'Guardar'" type="submit" color="primary" :loading="guardando" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogoMovimientoVisible">
      <q-card style="min-width: 350px">
        <q-card-section :class="nuevoMovimiento.tipo === 'ENTRADA' ? 'bg-positive text-white' : 'bg-negative text-white'">
          <div class="text-h6">{{ nuevoMovimiento.tipo === 'ENTRADA' ? 'Registrar Entrada' : 'Registrar Salida' }}</div>
          <div class="text-subtitle2">{{ productoSeleccionado?.nombre }}</div>
        </q-card-section>
        <q-card-section class="q-pt-md">
          <q-form @submit="guardarMovimiento" class="q-gutter-md">
            <q-input filled type="number" v-model.number="nuevoMovimiento.cantidad" label="Cantidad *" :rules="[ val => val > 0 || 'Mayor a 0', val => (nuevoMovimiento.tipo === 'SALIDA' ? val <= (productoSeleccionado?.stock_actual || 0) || 'Stock insuficiente' : true)]" />
            <q-input filled v-model="nuevoMovimiento.motivo" label="Motivo (Opcional)" />
            <div align="right">
              <q-btn flat label="Cancelar" v-close-popup />
              <q-btn :label="nuevoMovimiento.tipo === 'ENTRADA' ? 'Registrar Entrada' : 'Registrar Salida'" type="submit" :color="nuevoMovimiento.tipo === 'ENTRADA' ? 'positive' : 'negative'" :loading="guardando" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogoEliminarVisible">
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="warning" color="negative" text-color="white" />
          <span class="q-ml-sm">¿Seguro que quieres eliminar "{{ productoSeleccionado?.nombre }}"?</span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="primary" v-close-popup />
          <q-btn flat label="Eliminar" color="negative" @click="eliminarProductoRealmente" :loading="guardando" />
        </q-card-actions>
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

// --- ESTADO PRODUCTOS (CREAR/EDITAR/ELIMINAR) ---
const dialogoProductoVisible = ref(false)
const dialogoEliminarVisible = ref(false)
const modoEdicion = ref(false)
const idProductoEditar = ref(null)

const formProducto = reactive({
  nombre: '',
  codigo_sku: '',
  precio_costo: 0,
  precio_venta: 0,
  stock_minimo: 5
})

// --- ESTADO MOVIMIENTOS ---
const dialogoMovimientoVisible = ref(false)
const productoSeleccionado = ref(null)
const nuevoMovimiento = reactive({
  tipo: 'ENTRADA',
  cantidad: 1,
  motivo: '',
  producto_id: null
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'nombre', label: 'Nombre', field: 'nombre', sortable: true, align: 'left' },
  { name: 'sku', label: 'SKU', field: 'codigo_sku', align: 'left' },
  { name: 'precio_venta', label: 'Precio Venta', field: 'precio_venta', format: val => `$ ${val}` },
  { name: 'stock', label: 'Stock Actual', field: 'stock_actual', sortable: true },
  { name: 'acciones', label: 'Acciones', align: 'center' }
]

const cargarProductos = async () => {
  try {
    loading.value = true
    const response = await api.get('/productos/')
    productos.value = response.data
  } catch {
    $q.notify({ color: 'negative', message: 'Error al cargar inventario', icon: 'error' })
  } finally {
    loading.value = false
  }
}

// --- CREAR Y EDITAR ---
const resetFormProducto = () => {
  formProducto.nombre = ''
  formProducto.codigo_sku = ''
  formProducto.precio_costo = 0
  formProducto.precio_venta = 0
  formProducto.stock_minimo = 5
}

const abrirDialogoCrear = () => {
  modoEdicion.value = false
  resetFormProducto()
  dialogoProductoVisible.value = true
}

const abrirDialogoEditar = (producto) => {
  modoEdicion.value = true
  idProductoEditar.value = producto.id
  // Copiamos los datos del producto a editar al formulario
  formProducto.nombre = producto.nombre
  formProducto.codigo_sku = producto.codigo_sku
  formProducto.precio_costo = producto.precio_costo
  formProducto.precio_venta = producto.precio_venta
  formProducto.stock_minimo = producto.stock_minimo
  dialogoProductoVisible.value = true
}

const guardarProducto = async () => {
  try {
    guardando.value = true
    if (modoEdicion.value) {
      // ACTUALIZAR (PUT)
      await api.put(`/productos/${idProductoEditar.value}`, formProducto)
      $q.notify({ color: 'positive', message: 'Producto actualizado', icon: 'check' })
    } else {
      // CREAR (POST)
      await api.post('/productos/', formProducto)
      $q.notify({ color: 'positive', message: 'Producto creado', icon: 'check' })
    }
    dialogoProductoVisible.value = false
    cargarProductos()
  } catch (error) {
    const msj = error.response?.data?.detail || 'Error al guardar'
    $q.notify({ color: 'negative', message: msj, icon: 'report_problem' })
  } finally {
    guardando.value = false
  }
}

// --- ELIMINAR ---
const confirmarEliminar = (producto) => {
  productoSeleccionado.value = producto
  dialogoEliminarVisible.value = true
}

const eliminarProductoRealmente = async () => {
  try {
    guardando.value = true
    await api.delete(`/productos/${productoSeleccionado.value.id}`)
    $q.notify({ color: 'positive', message: 'Producto eliminado', icon: 'delete' })
    dialogoEliminarVisible.value = false
    cargarProductos()
  } catch {
    $q.notify({ color: 'negative', message: 'No se pudo eliminar el producto', icon: 'error' })
  } finally {
    guardando.value = false
  }
}

// --- MOVIMIENTOS ---
const abrirDialogoMovimiento = (tipo, producto) => {
  productoSeleccionado.value = producto
  nuevoMovimiento.tipo = tipo
  nuevoMovimiento.producto_id = producto.id
  nuevoMovimiento.cantidad = 1
  nuevoMovimiento.motivo = ''
  dialogoMovimientoVisible.value = true
}

const guardarMovimiento = async () => {
  try {
    guardando.value = true
    await api.post('/movimientos/', nuevoMovimiento)
    $q.notify({ color: 'positive', message: 'Movimiento registrado', icon: 'check' })
    dialogoMovimientoVisible.value = false
    cargarProductos()
  } catch (error) {
    const msj = error.response?.data?.detail || 'Error al registrar movimiento'
    $q.notify({ color: 'negative', message: msj, icon: 'report_problem' })
  } finally {
    guardando.value = false
  }
}

onMounted(() => {
  cargarProductos()
})
</script>