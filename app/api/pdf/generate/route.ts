import { NextRequest, NextResponse } from 'next/server';
import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import { readFile } from 'fs/promises';
import path from 'path';

// Coordinate maps matching the Python version
const COORDINATE_MAPS = {
    recepcion: {
        text: {
            center_name: { x: 125, y: 717 },
            service: { x: 125, y: 703 },
            manager: { x: 125, y: 690 },
            center_code: { x: 435, y: 717 },
            unit: { x: 380, y: 703 },
            floor: { x: 380, y: 690 },
            hole: { x: 485, y: 690 },
            description: { x: 130, y: 652 },
            brand: { x: 130, y: 638 },
            serial_number: { x: 130, y: 624 },
            provider: { x: 130, y: 610 },
            model: { x: 380, y: 638 },
            property: { x: 380, y: 624 },
            contact: { x: 380, y: 610 },
            reception_date: { x: 130, y: 572 },
            acceptance_date: { x: 290, y: 572 },
            warranty_end: { x: 445, y: 572 },
            periodicity: { x: 425, y: 543 },
            main_inventory_number: { x: 130, y: 370 },
            parent_inventory_number: { x: 365, y: 370 },
            order_number: { x: 420, y: 235 },
            amount_tax_included: { x: 420, y: 210 },
        },
        bools: {
            compliance: { truePos: { x: 290, y: 555 }, falsePos: { x: 320, y: 555 } },
            manuals_usage: { truePos: { x: 290, y: 545 }, falsePos: { x: 320, y: 545 } },
            manuals_tech: { truePos: { x: 290, y: 530 }, falsePos: { x: 320, y: 530 } },
            order_accordance: { truePos: { x: 290, y: 515 }, falsePos: { x: 320, y: 515 } },
            patient_data: { truePos: { x: 290, y: 500 }, falsePos: { x: 320, y: 500 } },
            backup_required: { truePos: { x: 290, y: 490 }, falsePos: { x: 320, y: 490 } },
            preventive_maintenance: { truePos: { x: 480, y: 555 }, falsePos: { x: 515, y: 555 } },
            maintenance_contract: { truePos: { x: 480, y: 530 }, falsePos: { x: 515, y: 530 } },
            received_correctly: { truePos: { x: 285, y: 248 }, falsePos: { x: 320, y: 248 } },
            users_trained: { truePos: { x: 285, y: 234 }, falsePos: { x: 320, y: 234 } },
            safe_to_use: { truePos: { x: 285, y: 221 }, falsePos: { x: 320, y: 221 } },
            requires_epis: { truePos: { x: 285, y: 207 }, falsePos: { x: 320, y: 207 } },
        },
        states: {
            good: { x: 255, y: 465 },
            bad: { x: 365, y: 465 },
            obsolete: { x: 480, y: 465 },
        },
        obs: { x: 60, startY: 430, minY: 400, width: 460 },
        table: { startY: 340, rowHeight: 18, cols: [60, 210, 300, 380, 440] },
    },
    baja: {
        text: {
            center_name: { x: 120, y: 696 },
            service: { x: 120, y: 683 },
            manager: { x: 120, y: 670 },
            center_code: { x: 425, y: 696 },
            unit: { x: 370, y: 683 },
            floor: { x: 370, y: 670 },
            hole: { x: 470, y: 670 },
            description: { x: 120, y: 622 },
            brand: { x: 120, y: 609 },
            serial_number: { x: 120, y: 596 },
            main_inventory_number: { x: 120, y: 583 },
            model: { x: 355, y: 609 },
            property: { x: 355, y: 596 },
            parent_inventory_number: { x: 355, y: 583 },
            baja_date: { x: 120, y: 534 },
            work_order_number: { x: 445, y: 234 },
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
                firstPage.drawText(String(value), {
                    x: coords.x,
                    y: coords.y,
                    size: fontSize,
                    font,
                    color: rgb(0, 0, 0),
                });
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
                if (comp.name) {
                    firstPage.drawText(String(comp.name).substring(0, 25), {
                        x: cols[0], y: currentY, size: 8, font, color: rgb(0, 0, 0),
                    });
                }
                if (comp.inventory) {
                    firstPage.drawText(String(comp.inventory).substring(0, 15), {
                        x: cols[1], y: currentY, size: 8, font, color: rgb(0, 0, 0),
                    });
                }
                if (comp.brand) {
                    firstPage.drawText(String(comp.brand).substring(0, 12), {
                        x: cols[2], y: currentY, size: 8, font, color: rgb(0, 0, 0),
                    });
                }
                if (comp.model) {
                    firstPage.drawText(String(comp.model).substring(0, 12), {
                        x: cols[3], y: currentY, size: 8, font, color: rgb(0, 0, 0),
                    });
                }
                if (comp.serial) {
                    firstPage.drawText(String(comp.serial).substring(0, 15), {
                        x: cols[4], y: currentY, size: 8, font, color: rgb(0, 0, 0),
                    });
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
