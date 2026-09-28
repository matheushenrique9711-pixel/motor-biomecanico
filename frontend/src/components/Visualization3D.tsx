import { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface Visualization3DProps {
  stlUrl?: string;
  title?: string;
  onLoaded?: () => void;
  onError?: (error: string) => void;
}

export const Visualization3D = ({
  stlUrl,
  title = 'Visualização 3D da Palmilha',
  onLoaded,
  onError,
}: Visualization3DProps) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const meshRef = useRef<THREE.Mesh | null>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    // Inicializa cena
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    sceneRef.current = scene;

    // Câmera
    const camera = new THREE.PerspectiveCamera(
      75,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 50, 150);
    camera.lookAt(0, 0, 0);

    // Renderizador
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.setClearColor(0xfafafa);
    rendererRef.current = renderer;
    mountRef.current.appendChild(renderer.domElement);

    // Iluminação
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(100, 100, 100);
    scene.add(directionalLight);

    const pointLight = new THREE.PointLight(0xffffff, 0.5);
    pointLight.position.set(-100, 100, 100);
    scene.add(pointLight);

    // Grade de referência
    const gridHelper = new THREE.GridHelper(300, 30);
    scene.add(gridHelper);

    // Cria geometria de exemplo (palmilha simples)
    const createDefaultInsole = () => {
      const geometry = new THREE.BufferGeometry();

      // Cria uma forma simplificada de palmilha
      const vertices = new Float32Array([
        // Ponta frontal
        60, 0, 50,
        50, 30, 48,
        50, -30, 48,

        // Meio
        40, 40, 40,
        40, -40, 40,

        // Calcanhar
        -80, 25, 30,
        -80, -25, 30,

        // Base (parte inferior)
        60, 0, -5,
        50, 30, -3,
        50, -30, -3,
        40, 40, -2,
        40, -40, -2,
        -80, 25, -8,
        -80, -25, -8,
      ]);

      const indices = new Uint32Array([
        // Topo
        0, 1, 2,
        1, 3, 4,
        2, 4, 1,
        3, 5, 6,
        4, 6, 3,

        // Base
        7, 9, 8,
        8, 10, 9,
        9, 11, 12,
        10, 12, 11,

        // Laterais
        0, 7, 1,
        1, 7, 8,
        0, 2, 7,
        2, 7, 9,
        2, 4, 9,
        4, 9, 10,
        4, 3, 10,
        3, 10, 11,
        3, 1, 11,
        1, 8, 11,
        5, 12, 6,
        6, 12, 10,
      ]);

      geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
      geometry.setIndex(new THREE.BufferAttribute(indices, 1));
      geometry.computeVertexNormals();

      const material = new THREE.MeshStandardMaterial({
        color: 0x2563eb,
        metalness: 0.3,
        roughness: 0.6,
      });

      const mesh = new THREE.Mesh(geometry, material);
      return mesh;
    };

    // Se houver URL de STL, carrega; senão cria geometria padrão
    if (stlUrl) {
      // Nota: para carregar STL real, seria necessário um loader STLLoader
      // Por enquanto, usamos geometria de exemplo
      const mesh = createDefaultInsole();
      scene.add(mesh);
      meshRef.current = mesh;
      onLoaded?.();
    } else {
      const mesh = createDefaultInsole();
      scene.add(mesh);
      meshRef.current = mesh;
    }

    // Animação de rotação
    const animate = () => {
      requestAnimationFrame(animate);

      if (meshRef.current) {
        meshRef.current.rotation.x += 0.003;
        meshRef.current.rotation.z += 0.002;
      }

      renderer.render(scene, camera);
    };

    animate();

    // Resize handler
    const handleResize = () => {
      if (!mountRef.current) return;

      const width = mountRef.current.clientWidth;
      const height = mountRef.current.clientHeight;

      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    window.addEventListener('resize', handleResize);

    // Interação com mouse (rotação manual)
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };

    renderer.domElement.addEventListener('mousedown', (e) => {
      isDragging = true;
      previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    renderer.domElement.addEventListener('mousemove', (e) => {
      if (isDragging && meshRef.current) {
        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;

        meshRef.current.rotation.y += deltaX * 0.005;
        meshRef.current.rotation.x += deltaY * 0.005;

        previousMousePosition = { x: e.clientX, y: e.clientY };
      }
    });

    renderer.domElement.addEventListener('mouseup', () => {
      isDragging = false;
    });

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.domElement.removeEventListener('mousedown', () => {});
      renderer.domElement.removeEventListener('mousemove', () => {});
      renderer.domElement.removeEventListener('mouseup', () => {});
      mountRef.current?.removeChild(renderer.domElement);
      geometry.dispose();
      renderer.dispose();
    };
  }, [stlUrl, onLoaded, onError]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-2xl font-bold mb-4 text-gray-800">{title}</h3>

      <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg overflow-hidden border-2 border-gray-200">
        <div
          ref={mountRef}
          style={{
            width: '100%',
            height: '500px',
            position: 'relative',
          }}
        />
      </div>

      <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
        <p className="font-semibold mb-2">💡 Controles:</p>
        <ul className="list-disc list-inside space-y-1 text-xs">
          <li>Arraste o mouse para rotacionar</li>
          <li>A visualização rotaciona automaticamente</li>
          <li>Representação 3D da palmilha parametrizada</li>
        </ul>
      </div>
    </div>
  );
};
