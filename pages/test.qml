import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import QtQuick.Shapes

Rectangle {
    id: musicWidget
    width: 320
    height: 200
    color: "#18181B"  // dark:bg-zinc-900
    radius: 8
    
    // Propriétés du widget
    property string songTitle: "Timro Mann"
    property string artistName: "Dibbya Subba"
    property bool isLiked: false
    property bool isFavorite: false
    property real progress: 0.5  // Entre 0 et 1
    property int duration: 215    // Durée totale en secondes
    property int currentTime: 3   // Temps actuel en secondes
    property bool isMuted: false
    
    // Fonction helper pour formater le temps
    function formatTime(seconds) {
        let minutes = Math.floor(seconds / 60)
        let remainingSeconds = seconds % 60
        return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // En-tête avec titre et icônes
        Rectangle {
            Layout.fillWidth: true
            height: 70
            color: "transparent"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                // Icône de musique
                Item {
                    Layout.preferredWidth: 24
                    Layout.preferredHeight: 24

                    Shape {
                        anchors.fill: parent
                        ShapePath {
                            strokeWidth: 2
                            strokeColor: "#EAB308"
                            fillColor: "transparent"
                            PathSvg { path: "M9 18V5l12-2v13 M6,18 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0 M18,16 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0" }
                        }
                    }
                }

                // Informations de la chanson
                ColumnLayout {
                    spacing: 4
                    Label {
                        text: songTitle
                        font.pixelSize: 18
                        color: "#E5E7EB"  // dark:text-gray-200
                    }
                    Label {
                        text: artistName
                        font.pixelSize: 14
                        color: "#9CA3AF"  // dark:text-gray-400
                    }
                }

                Item { Layout.fillWidth: true }  // Spacer

                // Icônes de droite
                Row {
                    spacing: 16
                    // Icône coeur
                    Item {
                        width: 24
                        height: 24
                        Shape {
                            anchors.fill: parent
                            ShapePath {
                                strokeWidth: 2
                                strokeColor: "#EF4444"
                                fillColor: isLiked ? "#EF4444" : "transparent"
                                PathSvg { path: "M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" }
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            onClicked: isLiked = !isLiked
                        }
                    }
                    // Icône étoile
                    Item {
                        width: 24
                        height: 24
                        Shape {
                            anchors.fill: parent
                            ShapePath {
                                strokeWidth: 2
                                strokeColor: "#9CA3AF"
                                fillColor: isFavorite ? "#EAB308" : "transparent"
                                PathSvg { path: "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" }
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            onClicked: isFavorite = !isFavorite
                        }
                    }
                }
            }
        }

        // Contrôles de lecture
        Rectangle {
            Layout.fillWidth: true
            Layout.margins: 16
            height: 60
            color: "transparent"

            ColumnLayout {
                anchors.fill: parent
                spacing: 8

                // Barre de progression
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    // Icône volume modifiée
                    Item {
                        width: 20
                        height: 20
                        Shape {
                            anchors.fill: parent
                            ShapePath {
                                strokeWidth: 2
                                strokeColor: "#9CA3AF"
                                fillColor: "transparent"
                                PathSvg { 
                                    path: isMuted ? 
                                        "M11 5L6 9H2v6h4l5 4V5z M23 9l-6 6 M17 9l6 6" :  // Icône mute
                                        "M11 5L6 9H2v6h4l5 4V5z M15 5a5 5 0 0 1 0 14"    // Icône volume
                                }
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            onClicked: isMuted = !isMuted
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 4
                        radius: 2
                        color: "#27272A"  // dark:bg-gray-800

                        Rectangle {
                            width: parent.width * progress
                            height: parent.height
                            color: "#EAB308"  // bg-yellow-500
                            radius: 2
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onMouseXChanged: {
                                if (pressed) {
                                    progress = Math.max(0, Math.min(1, mouseX / width))
                                    currentTime = Math.round(progress * duration)
                                }
                            }
                        }
                    }

                    Label {
                        text: Math.round(progress * 100) + "%"
                        font.pixelSize: 12
                        color: "#9CA3AF"
                    }
                }

                // Temps
                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: formatTime(currentTime)
                        font.pixelSize: 12
                        color: "#9CA3AF"
                    }
                    Item { Layout.fillWidth: true }
                    Label {
                        text: formatTime(duration)
                        font.pixelSize: 12
                        color: "#9CA3AF"
                    }
                }
            }
        }
    }
}
