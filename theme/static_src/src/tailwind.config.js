module.exports = {
    content: [
        // Cherche dans tous vos dossiers HTML à la racine ou dans vos apps
        '../templates/**/*.html',
        '../../**/templates/**/*.html',
        // Ajout spécifique pour votre dossier service
        '../../**/service/**/*.html',
    ],
    theme: {
        extend: {},
    },
    plugins: [],
}
