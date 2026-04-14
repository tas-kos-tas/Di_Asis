window.onload = function() {
    updateIndustryDescription();
    applySmartStyling();
};

function updateIndustryDescription() {
    const descriptions = {
        'technology': 'Programinė įranga, dirbtinis intelektas, kibernetinis saugumas, startuoliai',
        'finance': 'Bankininkystė, draudimas, investicijos, teisinės paslaugos, apskaita',
        'healthcare': 'Klinikos, farmacija, psichologija, odontologija, medicinos įranga',
        'fashion': 'Drabužiai, kosmetika, kirpyklos, juvelyrika, estetika',
        'education': 'Mokymai, kursai, universitetai, moksliniai tyrimai, EdTech',
        'entertainment': 'Renginiai, sporto klubai, menas, muzika, video žaidimai',
        'food': 'Restoranai, kavinės, maisto gamyba, viešbučiai, turizmas',
        'real_estate': 'NT agentūros, architektūra, interjero dizainas, statybų paslaugos',
        'logistics': 'Elektroninės parduotuvės, mažmeninė prekyba, transportas, sandėliavimas',
        'manufacturing': 'Sunkioji ir lengvoji pramonė, inžinerija, baldų gamyba, žaliavos',
        'ecology': 'Atsinaujinanti energija, tvarumas, žemės ūkis, aplinkosauga',
        'services': 'Konsultavimas, marketingas, personalo atranka, kūrybinės paslaugos',
        'ngo': 'Valstybinės įstaigos, labdaros fondai, bendruomenės, asociacijos',
        'other': 'Jei jūsų veikla unikali – mielai apie ją išgirsiu plačiau!'
    };
    const select = document.getElementById('industrySelect');
    const descDiv = document.getElementById('industryDesc');
    
    if (select && descDiv) {
        descDiv.innerText = descriptions[select.value] || '';
    }
}

function applySmartStyling() {
    const colorBoxes = document.querySelectorAll('.color-box');
    let colors = Array.from(colorBoxes).map(c => rgbToHex(c.style.backgroundColor));

    if (colors.length > 0) {
        // Rūšiuojame spalvas nuo TAMSIAUSIOS iki ŠVIESIAUSIOS
        let sortedColors = [...colors].sort((a, b) => getLuminance(a) - getLuminance(b));

        // 1. Tamsiausia spalva -> Hero banerio fonui
        document.documentElement.style.setProperty('--primary-tint', sortedColors[0]);
        
        // 2. Antra tamsiausia spalva -> Mygtukui
        document.documentElement.style.setProperty('--accent-color', sortedColors[1]);

        // 3. Vidurinė spalva -> Apatiniam font demo blokui
        document.documentElement.style.setProperty('--demo-bg', sortedColors[2]);
        
        // Apatinio bloko tekstui parenkame juodą arba baltą spalvą pagal fono šviesumą
        const demoTextColor = getLuminance(sortedColors[2]) > 128 ? '#111111' : '#FFFFFF';
        document.documentElement.style.setProperty('--demo-text', demoTextColor);

        // 4. Sutvarkome HEX kodų teksto spalvas viduje kiekvieno stačiakampio
        colorBoxes.forEach(box => {
            const hex = rgbToHex(box.style.backgroundColor);
            box.style.color = getLuminance(hex) > 128 ? '#111111' : '#FFFFFF';
        });
    }
}

// Matematika šviesumui apskaičiuoti
function getLuminance(hex) {
    const rgb = hexToRgb(hex);
    return (rgb.r * 0.299 + rgb.g * 0.587 + rgb.b * 0.114);
}

function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? { r: parseInt(result[1], 16), g: parseInt(result[2], 16), b: parseInt(result[3], 16) } : { r: 0, g: 0, b: 0 };
}

function rgbToHex(rgb) {
    if (rgb.startsWith('#')) return rgb;
    const parts = rgb.match(/\d+/g);
    return "#" + parts.map(x => parseInt(x).toString(16).padStart(2, '0')).join('');
}