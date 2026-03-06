/**
 * Script de generación de PDF usando Puppeteer
 * Sistema SAC WEB
 * 
 * Este script recibe una URL, la abre con Chromium y genera un PDF.
 * 
 * Uso:
 *   node scripts/generate_pdf.js <url> <output_path>
 * 
 * Ejemplo:
 *   node scripts/generate_pdf.js "http://127.0.0.1:8000/recibos/..." "temp/recibo.pdf"
 */

const puppeteer = require('puppeteer');
const path = require('path');

// Obtener argumentos de línea de comandos
const args = process.argv.slice(2);

if (args.length < 2) {
    console.error('Error: Se requieren 2 argumentos');
    console.error('Uso: node generate_pdf.js <url> <output_path>');
    process.exit(1);
}

const url = args[0];
const outputPath = args[1];

/**
 * Función principal de generación de PDF
 */
async function generatePDF() {
    let browser = null;
    
    try {
        console.log('Iniciando Puppeteer...');
        
        // Lanzar navegador
        browser = await puppeteer.launch({
            headless: 'new',  // Modo headless (sin interfaz gráfica)
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ]
        });
        
        console.log('Navegador iniciado');
        
        // Crear nueva página
        const page = await browser.newPage();
        
        console.log(`Navegando a: ${url}`);
        
        // Navegar a la URL
        // waitUntil: 'networkidle0' espera a que no haya conexiones de red activas
        await page.goto(url, {
            waitUntil: 'networkidle0',
            timeout: 30000  // 30 segundos de timeout
        });
        
        console.log('Página cargada completamente');
        
        // Generar PDF
        console.log('Generando PDF...');
        
        await page.pdf({
            path: outputPath,
            format: 'A4',
            printBackground: true,  // Incluir colores y fondos
            margin: {
                top: '1cm',
                right: '1cm',
                bottom: '1cm',
                left: '1cm'
            }
        });
        
        console.log(`PDF generado exitosamente: ${outputPath}`);
        
        // Cerrar navegador
        await browser.close();
        
        // Salir con código 0 (éxito)
        process.exit(0);
        
    } catch (error) {
        console.error('Error al generar PDF:', error.message);
        
        // Cerrar navegador si está abierto
        if (browser) {
            await browser.close();
        }
        
        // Salir con código 1 (error)
        process.exit(1);
    }
}

// Ejecutar función principal
generatePDF();
