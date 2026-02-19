<?php
// API REST simple
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$data = [
    'boe' => json_decode(file_get_contents('../datos/boe.json'), true),
    'alertas' => json_decode(file_get_contents('../datos/alertas.json'), true),
    'subvenciones' => json_decode(file_get_contents('../datos/subvenciones.json'), true),
    'gasto' => json_decode(file_get_contents('../datos/gasto.json'), true),
    'promesas' => json_decode(file_get_contents('../datos/promesas.json'), true),
    'metadata' => [
        'fecha_actualizacion' => date('Y-m-d H:i:s'),
        'version' => '1.0.0'
    ]
];

echo json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
