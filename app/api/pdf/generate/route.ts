import { NextRequest, NextResponse } from 'next/server';
import { PDFDocument, StandardFonts, rgb, PDFPage, PDFFont } from 'pdf-lib';
import { readFile } from 'fs/promises';
import path from 'path';

// Coordinate maps matching the Python version
const COORDINATE_MAPS = {
    recepcion: {
        text: {
            center_name: { x: 125, y: 717, maxWidth: 247.5 },
            service: { x: 125, y: 703, maxWidth: 202.9 },
            manager: { x: 125, y: 690, maxWidth: 202.9 },
            center_code: { x: 435, y: 717, maxWidth: 115.0 },
            unit: { x: 380, y: 703, maxWidth: 170.0 },
            floor: { x: 380, y: 690, maxWidth: 66.1 },
            hole: { x: 485, y: 690, maxWidth: 65.0 },
            description: { x: 130, y: 652, maxWidth: 420.0 },
            brand: { x: 130, y: 638, maxWidth: 197.9 },
            serial_number: { x: 130, y: 624, maxWidth: 197.9 },
            provider: { x: 130, y: 610, maxWidth: 197.9 },
            model: { x: 380, y: 638, maxWidth: 170.0 },
            property: { x: 380, y: 624, maxWidth: 170.0 },
            contact: { x: 380, y: 610, maxWidth: 170.0 },
            reception_date: { x: 130, y: 572, maxWidth: 90.1 },
            acceptance_date: { x: 290, y: 572, maxWidth: 82.5 },
            warranty_end: { x: 445, y: 572, maxWidth: 105.0 },
            periodicity: { x: 425, y: 543, maxWidth: 125.0 },
            main_inventory_number: { x: 130, y: 370, maxWidth: 149.2 },
            parent_inventory_number: { x: 365, y: 370, maxWidth: 185.0 },
            order_number: { x: 420, y: 235, maxWidth: 130.0 },
            amount_tax_included: { x: 420, y: 210, maxWidth: 130.0 },
        },
        bools: {
            compliance: { truePos: { x: 285, y: 555 }, falsePos: { x: 320, y: 555 } },
            manuals_usage: { truePos: { x: 285, y: 545 }, falsePos: { x: 320, y: 545 } },
            manuals_tech: { truePos: { x: 285, y: 530 }, falsePos: { x: 320, y: 530 } },
            order_accordance: { truePos: { x: 285, y: 515 }, falsePos: { x: 320, y: 515 } },
            patient_data: { truePos: { x: 285, y: 500 }, falsePos: { x: 320, y: 500 } },
            backup_required: { truePos: { x: 285, y: 490 }, falsePos: { x: 320, y: 490 } },
            preventive_maintenance: { truePos: { x: 480, y: 555 }, falsePos: { x: 515, y: 555 } },
            maintenance_contract: { truePos: { x: 480, y: 530 }, falsePos: { x: 515, y: 530 } },
            received_correctly: { truePos: { x: 285, y: 248 }, falsePos: { x: 320, y: 248 } },
            users_trained: { truePos: { x: 285, y: 234 }, falsePos: { x: 320, y: 234 } },
            safe_to_use: { truePos: { x: 285, y: 221 }, falsePos: { x: 320, y: 221 } },
            requires_epis: { truePos: { x: 285, y: 207 }, falsePos: { x: 320, y: 207 } },
        },
        states: {
            good: { x: 255, y: 470 },
            bad: { x: 365, y: 470 },
            obsolete: { x: 480, y: 470 },
        },
        obs: { x: 60, startY: 430, minY: 400, width: 460 },
        table: { startY: 340, rowHeight: 14, cols: [60, 210, 300, 380, 440], colsWidth: [140, 80, 70, 50, 105] },
    },
    baja: {
        text: {
            center_name: { x: 120, y: 696, maxWidth: 243.9 },
            service: { x: 120, y: 683, maxWidth: 205.9 },
            manager: { x: 120, y: 670, maxWidth: 202.9 },
            center_code: { x: 425, y: 696, maxWidth: 105.0 },
            unit: { x: 370, y: 683, maxWidth: 160.0 },
            floor: { x: 370, y: 670, maxWidth: 48.0 },
            hole: { x: 470, y: 670, maxWidth: 60.0 },
            description: { x: 120, y: 622, maxWidth: 410.0 },
            brand: { x: 120, y: 609, maxWidth: 189.4 },
            serial_number: { x: 120, y: 596, maxWidth: 189.4 },
            main_inventory_number: { x: 120, y: 583, maxWidth: 121.9 },
            model: { x: 355, y: 609, maxWidth: 175.0 },
            property: { x: 355, y: 596, maxWidth: 175.0 },
            parent_inventory_number: { x: 355, y: 583, maxWidth: 175.0 },
            baja_date: { x: 120, y: 534, maxWidth: 410.0 },
            work_order_number: { x: 425, y: 234, maxWidth: 105.0 },
        },
        bools: {
            repair_budget: { truePos: { x: 270, y: 234 }, falsePos: { x: 300, y: 234 } },
            replacement_budget: { truePos: { x: 270, y: 221 }, falsePos: { x: 300, y: 221 } },
            sat_report: { truePos: { x: 270, y: 208 }, falsePos: { x: 300, y: 208 } },
            other_docs: { truePos: { x: 270, y: 195 }, falsePos: { x: 300, y: 195 } },
            data_cleaned: { truePos: { x: 270, y: 182 }, falsePos: { x: 300, y: 182 } },
        },
        states: {} as Record<string, { x: number; y: number }>,
        obs: { x: 60, startY: 370, minY: 280, width: 440 },
        justification: { x: 60, startY: 510, minY: 420, width: 440 },
        table: null,
    },
};

function drawFittedText(page: PDFPage, text: string, x: number, y: number, maxWidth: number, font: PDFFont, defaultSize: number, color: any) {
    let size = defaultSize;
    let fittedText = text;
    let textWidth = font.widthOfTextAtSize(fittedText, size);

    if (textWidth <= maxWidth) {
        page.drawText(fittedText, { x, y, size, font, color });
        return;
    }

    while (size > 6 && textWidth > maxWidth) {
        size -= 0.5;
        textWidth = font.widthOfTextAtSize(fittedText, size);
    }

    if (textWidth > maxWidth) {
        while (fittedText.length > 0 && font.widthOfTextAtSize(fittedText + '...', size) > maxWidth) {
            fittedText = fittedText.slice(0, -1);
        }
        fittedText += '...';
    }

    page.drawText(fittedText, { x, y, size, font, color });
}

export async function POST(request: NextRequest) {
    try {
        const { data, reportType = 'recepcion' } = await request.json();

        // Load the template PDF
        const templatePath = path.join(
            process.cwd(),
            'public',
            'templates',
            reportType === 'baja' ? 'baja.pdf' : 'recepcion.pdf'
        );

        let templateBytes: Uint8Array;
        try {
            templateBytes = await readFile(templatePath);
        } catch (e) {
            console.error('Template not found:', templatePath);
            return NextResponse.json(
                { error: `Template not found: ${reportType}.pdf` },
                { status: 404 }
            );
        }

        const pdfDoc = await PDFDocument.load(templateBytes);
        const pages = pdfDoc.getPages();
        const firstPage = pages[0];
        const font = await pdfDoc.embedFont(StandardFonts.Helvetica);

        const config: any = COORDINATE_MAPS[reportType as keyof typeof COORDINATE_MAPS];
        const fontSize = 10;

        // Draw text fields
        for (const [key, coords] of Object.entries(config.text) as [string, any][]) {
            const value = data[key];
            if (value !== undefined && value !== null && value !== '') {
                drawFittedText(
                    firstPage,
                    String(value),
                    coords.x,
                    coords.y,
                    coords.maxWidth || 200, // exact mapped coordinates or fallback
                    font,
                    fontSize,
                    rgb(0, 0, 0)
                );
            }
        }

        // Draw boolean checkmarks
        for (const [key, positions] of Object.entries(config.bools) as [string, any][]) {
            const value = data[key];
            if (value === true) {
                firstPage.drawText('X', {
                    x: positions.truePos.x,
                    y: positions.truePos.y,
                    size: fontSize,
                    font,
                    color: rgb(0, 0, 0),
                });
            } else if (value === false) {
                firstPage.drawText('X', {
                    x: positions.falsePos.x,
                    y: positions.falsePos.y,
                    size: fontSize,
                    font,
                    color: rgb(0, 0, 0),
                });
            }
        }

        // Draw equipment status
        if (data.equipment_status && config.states) {
            const statusKey = data.equipment_status.toLowerCase();
            const statusPos = config.states[statusKey as keyof typeof config.states];
            if (statusPos) {
                firstPage.drawText('X', {
                    x: statusPos.x,
                    y: statusPos.y,
                    size: fontSize,
                    font,
                    color: rgb(0, 0, 0),
                });
            }
        }

        // Draw observations
        if (data.observations && config.obs) {
            const obsText = data.observations;
            let currentY = config.obs.startY;
            const words = obsText.split(' ');
            let currentLine = '';

            for (const word of words) {
                const testLine = currentLine ? `${currentLine} ${word}` : word;
                const textWidth = font.widthOfTextAtSize(testLine, fontSize);

                if (textWidth > (config.obs.width || 400)) {
                    firstPage.drawText(currentLine, {
                        x: config.obs.x,
                        y: currentY,
                        size: fontSize,
                        font,
                        color: rgb(0, 0, 0),
                    });
                    currentY -= fontSize + 2;
                    currentLine = word;
                } else {
                    currentLine = testLine;
                }
            }

            if (currentLine) {
                firstPage.drawText(currentLine, {
                    x: config.obs.x,
                    y: currentY,
                    size: fontSize,
                    font,
                    color: rgb(0, 0, 0),
                });
            }
        }

        // Draw justification (baja only)
        if (reportType === 'baja' && data.justification_report && config.justification) {
            const justText = data.justification_report;
            let currentY = config.justification.startY;
            const words = justText.split(' ');
            let currentLine = '';

            for (const word of words) {
                const testLine = currentLine ? `${currentLine} ${word}` : word;
                const textWidth = font.widthOfTextAtSize(testLine, fontSize);

                if (textWidth > (config.justification.width || 400)) {
                    firstPage.drawText(currentLine, {
                        x: config.justification.x,
                        y: currentY,
                        size: fontSize,
                        font,
                        color: rgb(0, 0, 0),
                    });
                    currentY -= fontSize + 2;
                    currentLine = word;
                } else {
                    currentLine = testLine;
                }
            }

            if (currentLine) {
                firstPage.drawText(currentLine, {
                    x: config.justification.x,
                    y: currentY,
                    size: fontSize,
                    font,
                    color: rgb(0, 0, 0),
                });
            }
        }

        // Draw components table (recepcion only)
        if (reportType === 'recepcion' && data.components && config.table) {
            const components = data.components;
            let currentY = config.table.startY;

            for (const comp of components) {
                if (currentY < 50) break;

                const cols = config.table.cols;
                const colsWidth = config.table.colsWidth;

                if (comp.name) {
                    drawFittedText(firstPage, String(comp.name), cols[0], currentY, colsWidth[0], font, 8, rgb(0, 0, 0));
                }
                if (comp.inventory) {
                    drawFittedText(firstPage, String(comp.inventory), cols[1], currentY, colsWidth[1], font, 8, rgb(0, 0, 0));
                }
                if (comp.brand) {
                    drawFittedText(firstPage, String(comp.brand), cols[2], currentY, colsWidth[2], font, 8, rgb(0, 0, 0));
                }
                if (comp.model) {
                    drawFittedText(firstPage, String(comp.model), cols[3], currentY, colsWidth[3], font, 8, rgb(0, 0, 0));
                }
                if (comp.serial) {
                    drawFittedText(firstPage, String(comp.serial), cols[4], currentY, colsWidth[4], font, 8, rgb(0, 0, 0));
                }

                currentY -= config.table.rowHeight;
            }
        }

        const pdfBytes = await pdfDoc.save();

        return new NextResponse(Buffer.from(pdfBytes), {
            headers: {
                'Content-Type': 'application/pdf',
                'Content-Disposition': `attachment; filename="Acta_${reportType}_${Date.now()}.pdf"`,
            },
        });
    } catch (error) {
        console.error('Error generating PDF:', error);
        return NextResponse.json(
            { error: 'Failed to generate PDF' },
            { status: 500 }
        );
    }
}
