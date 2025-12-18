import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Alert,
  AlertIcon,
  Box,
  Button,
  Container,
  Divider,
  Flex,
  Heading,
  HStack,
  Input,
  Select,
  Spinner,
  Tag,
  Text,
  VStack,
} from '@chakra-ui/react'
import { MapContainer, Marker, Polyline, Rectangle, Tooltip } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import './App.css'
import { api } from './api'
import type { Device, Layout, LayoutDevice, Link } from './api'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
})

type LayoutWithDevices = Layout & {
  devicesDetailed: Array<Layout['devices'][number] & { device?: Device }>
}

const bounds: L.LatLngBoundsExpression = [
  [0, 0],
  [1, 1],
]

function App() {
  const [devices, setDevices] = useState<Device[]>([])
  const [layouts, setLayouts] = useState<Layout[]>([])
  const [links, setLinks] = useState<Link[]>([])
  const [selectedLayoutId, setSelectedLayoutId] = useState<string | undefined>(undefined)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editingDevices, setEditingDevices] = useState<LayoutDevice[]>([])
  const [newDeviceForm, setNewDeviceForm] = useState({ name: '', ip: '', type: 'host' })

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [deviceResp, layoutResp, linkResp] = await Promise.all([
        api.getDevices(),
        api.getLayouts(),
        api.getLinks(),
      ])
      setDevices(deviceResp)
      setLayouts(layoutResp)
      setLinks(linkResp)
      if (!selectedLayoutId && layoutResp.length > 0) {
        setSelectedLayoutId(layoutResp[0].id)
      }
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const currentLayout: LayoutWithDevices | undefined = useMemo(() => {
    const layout = layouts.find((l) => l.id === selectedLayoutId) ?? layouts[0]
    if (!layout) return undefined
    const deviceMap = new Map(devices.map((d) => [d.id, d]))
    return {
      ...layout,
      devicesDetailed: layout.devices.map((d) => ({
        ...d,
        device: deviceMap.get(d.device_id),
      })),
    }
  }, [devices, layouts, selectedLayoutId])

  useEffect(() => {
    if (currentLayout) {
      setEditingDevices(currentLayout.devices)
    } else {
      setEditingDevices([])
    }
  }, [currentLayout])

  const linkLines = useMemo(() => {
    if (!currentLayout) return []
    const coordMap = new Map(editingDevices.map((d) => [d.device_id, [d.y, d.x] as [number, number]]))
    return links
      .map((link) => {
        const from = coordMap.get(link.source_device_id)
        const to = coordMap.get(link.target_device_id)
        if (!from || !to) return null
        return { id: link.id, from, to, label: link.label }
      })
      .filter(Boolean) as Array<{ id: string; from: [number, number]; to: [number, number]; label?: string | null }>
  }, [editingDevices, links, currentLayout])

  const handleMarkerDrag = useCallback((deviceId: string, lat: number, lng: number) => {
    setEditingDevices((prev) =>
      prev.map((d) => (d.device_id === deviceId ? { ...d, x: lng, y: lat } : d)),
    )
  }, [])

  const handleSaveLayout = async () => {
    if (!currentLayout) return
    setSaving(true)
    setError(null)
    try {
      await api.updateLayout(currentLayout.id, {
        name: currentLayout.name,
        background: currentLayout.background,
        devices: editingDevices,
      })
      await fetchData()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  const handleCreateLayout = async () => {
    const timestamp = new Date().toISOString().slice(0, 19).replace('T', ' ')
    setSaving(true)
    setError(null)
    try {
      const created = await api.createLayout({
        name: `Layout ${timestamp}`,
        background: 'osm',
        devices: [],
      })
      setLayouts((prev) => [...prev, created])
      setSelectedLayoutId(created.id)
      setEditingDevices([])
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  const handleAddDevice = async () => {
    if (!currentLayout) {
      setError('Create or select a layout before adding devices.')
      return
    }
    if (!newDeviceForm.name || !newDeviceForm.ip) {
      setError('Name and IP are required to add a device.')
      return
    }
    setSaving(true)
    setError(null)
    try {
      const created = await api.createDevice({
        name: newDeviceForm.name,
        ip_address: newDeviceForm.ip,
        type: newDeviceForm.type,
      })
      const updatedPlacements = [...editingDevices, { device_id: created.id, x: 0.5, y: 0.5 }]
      setDevices((prev) => [...prev, created])
      setLayouts((prev) =>
        prev.map((l) => (l.id === currentLayout.id ? { ...l, devices: updatedPlacements } : l)),
      )
      setEditingDevices(updatedPlacements)
      setNewDeviceForm({ name: '', ip: '', type: 'host' })
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Container maxW="6xl" py={6}>
      <Flex justify="space-between" align={{ base: 'flex-start', md: 'center' }} gap={4} flexDir={{ base: 'column', md: 'row' }}>
        <Box>
          <Heading size="lg">MonoTaur Map Prototype</Heading>
          <Text color="gray.400">Leaflet + Chakra UI wired to the FastAPI mock backend</Text>
        </Box>
        <HStack spacing={3} alignSelf={{ base: 'stretch', md: 'center' }} flexWrap="wrap">
          <Select
            value={currentLayout?.id ?? ''}
            onChange={(e) => setSelectedLayoutId(e.target.value)}
            placeholder="Choose a layout"
            minW="200px"
            bg="gray.900"
          >
            {layouts.map((layout) => (
              <option key={layout.id} value={layout.id}>
                {layout.name}
              </option>
            ))}
          </Select>
          <Button onClick={fetchData} isLoading={loading} colorScheme="teal" variant="outline">
            Refresh
          </Button>
          <Button onClick={handleCreateLayout} isLoading={saving} colorScheme="purple">
            New layout
          </Button>
          <Button onClick={handleSaveLayout} isLoading={saving} colorScheme="teal" variant="solid" isDisabled={!currentLayout}>
            Save layout
          </Button>
        </HStack>
      </Flex>

      <Divider my={5} />

      {error && (
        <Alert status="error" mb={4}>
          <AlertIcon />
          {error}
        </Alert>
      )}

      <Flex gap={6} direction={{ base: 'column', lg: 'row' }}>
        <Box flex="1" minH="420px" bg="gray.900" borderWidth="1px" borderColor="gray.700" borderRadius="lg" overflow="hidden">
          {loading && (
            <Flex height="100%" align="center" justify="center">
              <Spinner size="lg" />
            </Flex>
          )}
          {!loading && currentLayout && (
            <MapContainer
              key={currentLayout.id}
              crs={L.CRS.Simple}
              bounds={bounds}
              maxBounds={bounds}
              center={[0.5, 0.5]}
              zoom={0}
              minZoom={-4}
              maxZoom={2}
              scrollWheelZoom
              className="map-shell"
            >
              <Rectangle bounds={bounds} pathOptions={{ color: '#38B2AC', weight: 1, fillOpacity: 0.02 }} />
              {editingDevices.map((placement) => {
                const details = currentLayout.devicesDetailed.find((d) => d.device_id === placement.device_id)
                return (
                  <Marker
                    key={placement.device_id}
                    position={[placement.y, placement.x]}
                    draggable
                    eventHandlers={{
                      dragend: (e) => {
                        const { lat, lng } = (e as L.LeafletEvent & { target: L.Marker }).target.getLatLng()
                        handleMarkerDrag(placement.device_id, lat, lng)
                      },
                    }}
                  >
                    <Tooltip direction="top" offset={[0, -10]} opacity={1}>
                      <Box>
                        <Text fontWeight="bold">{details?.device?.name ?? 'Unnamed device'}</Text>
                        <Text fontSize="xs" color="gray.200">
                          {details?.device?.ip_address ?? 'No IP'} · {details?.device?.type ?? 'unknown'}
                        </Text>
                      </Box>
                    </Tooltip>
                  </Marker>
                )
              })}
              {linkLines.map((link) => (
                <Polyline key={link.id} positions={[link.from, link.to]} pathOptions={{ color: '#90cdf4', weight: 3, opacity: 0.8 }}>
                  {link.label && (
                    <Tooltip sticky direction="center">
                      <Text fontSize="xs">{link.label}</Text>
                    </Tooltip>
                  )}
                </Polyline>
              ))}
            </MapContainer>
          )}
          {!loading && !currentLayout && (
            <Flex height="100%" align="center" justify="center" p={6}>
              <Text color="gray.400">No layouts found. Create one to start placing devices.</Text>
            </Flex>
          )}
        </Box>

        <Box w={{ base: '100%', lg: '360px' }} bg="gray.900" borderWidth="1px" borderColor="gray.700" borderRadius="lg" p={4}>
          <Heading size="md" mb={3}>
            Layout details
          </Heading>
          {currentLayout ? (
            <VStack align="stretch" spacing={3}>
              <Box>
                <Text fontWeight="semibold">{currentLayout.name}</Text>
                <Text fontSize="sm" color="gray.400">
                  Background: {currentLayout.background}
                </Text>
              </Box>
              <Divider />
              <Text fontSize="sm" color="gray.400" mb={1}>
                Add device
              </Text>
              <VStack align="stretch" spacing={2} bg="gray.800" borderRadius="md" p={3}>
                <HStack>
                  <Input
                    size="sm"
                    placeholder="Name"
                    value={newDeviceForm.name}
                    onChange={(e) => setNewDeviceForm((prev) => ({ ...prev, name: e.target.value }))}
                  />
                  <Input
                    size="sm"
                    placeholder="IP (e.g., 192.0.2.10)"
                    value={newDeviceForm.ip}
                    onChange={(e) => setNewDeviceForm((prev) => ({ ...prev, ip: e.target.value }))}
                  />
                </HStack>
                <HStack>
                  <Input
                    size="sm"
                    placeholder="Type (router/switch/host)"
                    value={newDeviceForm.type}
                    onChange={(e) => setNewDeviceForm((prev) => ({ ...prev, type: e.target.value }))}
                  />
                  <Button size="sm" colorScheme="teal" onClick={handleAddDevice} isLoading={saving} flexShrink={0}>
                    Add
                  </Button>
                </HStack>
                <Text fontSize="xs" color="gray.500">
                  Devices start at map center; drag markers to reposition before saving the layout.
                </Text>
              </VStack>
              <Divider />
              <Text fontSize="sm" color="gray.400">
                Devices in layout
              </Text>
              {editingDevices.length === 0 && <Text color="gray.500">No devices placed yet.</Text>}
              {editingDevices.map((item) => {
                const device = devices.find((d) => d.id === item.device_id)
                return (
                  <Box
                    key={item.device_id}
                    borderWidth="1px"
                    borderColor="gray.700"
                    borderRadius="md"
                    p={3}
                    bg="gray.800"
                  >
                    <HStack justify="space-between">
                      <Text fontWeight="semibold">{device?.name ?? 'Unknown device'}</Text>
                      <Tag size="sm" colorScheme="cyan">
                        {device?.type ?? 'unknown'}
                      </Tag>
                    </HStack>
                    <Text fontSize="sm" color="gray.400">
                      {device?.ip_address ?? 'No IP'}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      Position: x {item.x.toFixed(2)}, y {item.y.toFixed(2)}
                    </Text>
                  </Box>
                )
              })}
              <Divider />
              <Text fontSize="sm" color="gray.400">
                Links on map
              </Text>
              {linkLines.length === 0 && <Text color="gray.500">No links for this layout.</Text>}
              {linkLines.map((link) => (
                <Box key={link.id} borderWidth="1px" borderColor="gray.700" borderRadius="md" p={3} bg="gray.800">
                  <Text fontWeight="semibold" fontSize="sm">
                    {link.label ?? 'Link'}
                  </Text>
                  <Text fontSize="xs" color="gray.400">
                    {link.from.join(', ')} {'->'} {link.to.join(', ')}
                  </Text>
                </Box>
              ))}
            </VStack>
          ) : (
            <Text color="gray.500">No layouts loaded.</Text>
          )}
        </Box>
      </Flex>
    </Container>
  )
}

export default App
