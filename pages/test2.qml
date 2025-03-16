import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: themeSwitch
    width: 169 // 5.625em * 30px
    height: 75 // 2.5em * 30px
    color: checked ? "#1D1F2C" : "#3D7EAE"
    radius: 187 // 6.25em * 30px
    
    property bool checked: false
    
    // Propriétés
    property real toggleSize: 30
    property real circleContainerSize: 101 // 3.375em * 30px
    property real sunMoonSize: 64 // 2.125em * 30px
    
    // Ajouter une transition pour la couleur de fond
    Behavior on color {
        ColorAnimation {
            duration: 300
            easing.type: Easing.OutCubic
        }
    }
    
    // Conteneur du cercle
    Rectangle {
        id: circleContainer
        width: parent.height + 26
        height: width
        radius: width/2
        color: "transparent"
        
        x: checked ? parent.width - width - (-13) : -13
        anchors.verticalCenter: parent.verticalCenter  // Centrer verticalement
        
        // Animation de déplacement
        Behavior on x {
            NumberAnimation { 
                duration: 300
                easing.type: Easing.OutCubic
            }
        }
        
        // Soleil/Lune
        Rectangle {
            id: sunMoon
            width: sunMoonSize
            height: width
            radius: width/2
            anchors.centerIn: parent
            color: checked ? "#C4C9D1" : "#ECCA2F"
            
            // Ajouter une transition pour la couleur du soleil/lune
            Behavior on color {
                ColorAnimation {
                    duration: 300
                    easing.type: Easing.OutCubic
                }
            }
            
            // Points de la lune
            Rectangle {
                visible: checked
                opacity: checked ? 1 : 0  // Ajouter une opacité pour la transition
                width: 22
                height: width
                radius: width/2
                color: "#959DB1"
                x: 9
                y: 22
                
                // Transition pour l'opacité
                Behavior on opacity {
                    NumberAnimation {
                        duration: 300
                        easing.type: Easing.OutCubic
                    }
                }
            }
            
            Rectangle {
                visible: checked
                opacity: checked ? 1 : 0
                width: 11
                height: width
                radius: width/2
                color: "#959DB1"
                x: 41
                y: 28
                
                Behavior on opacity {
                    NumberAnimation {
                        duration: 300
                        easing.type: Easing.OutCubic
                    }
                }
            }
            
            Rectangle {
                visible: checked
                opacity: checked ? 1 : 0
                width: 7
                height: width
                radius: width/2
                color: "#959DB1"
                x: 24
                y: 9
                
                Behavior on opacity {
                    NumberAnimation {
                        duration: 300
                        easing.type: Easing.OutCubic
                    }
                }
            }
        }
        
        // Nuages améliorés
        Item {
            visible: !checked
            opacity: checked ? 0 : 1  // Ajouter une opacité pour la transition
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: sunMoon.right
            anchors.leftMargin: 10  // Réduit la marge
            width: 80  // Réduit la largeur du conteneur
            height: 40  // Réduit la hauteur
            
            // Premier groupe de nuages
            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                spacing: -12  // Réduit l'espacement
                Rectangle {
                    width: 35  // Réduit les tailles
                    height: 20
                    radius: height/2
                    color: "#F3FDFF"
                }
                Rectangle {
                    width: 25
                    height: 15
                    radius: height/2
                    color: "#F3FDFF"
                    y: 5
                }
                Rectangle {
                    width: 30
                    height: 17
                    radius: height/2
                    color: "#F3FDFF"
                    y: 2
                }
            }
            
            // Deuxième groupe de nuages
            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                anchors.verticalCenterOffset: -8
                spacing: -8
                Rectangle {
                    width: 22
                    height: 14
                    radius: height/2
                    color: "#F3FDFF"
                    opacity: 0.8
                }
                Rectangle {
                    width: 18
                    height: 12
                    radius: height/2
                    color: "#F3FDFF"
                    opacity: 0.8
                    y: 3
                }
            }
            
            // Ajouter la transition pour l'opacité
            Behavior on opacity {
                NumberAnimation {
                    duration: 300
                    easing.type: Easing.OutCubic
                }
            }
        }
        
        // Étoiles
        Grid {
            visible: checked
            opacity: checked ? 1 : 0  // Ajouter une opacité pour la transition
            columns: 3
            spacing: 15
            anchors.centerIn: parent
            
            Repeater {
                model: 5
                Rectangle {
                    width: 4
                    height: width
                    radius: width/2
                    color: "white"
                }
            }
            
            // Ajouter la transition pour l'opacité
            Behavior on opacity {
                NumberAnimation {
                    duration: 300
                    easing.type: Easing.OutCubic
                }
            }
        }
    }
    
    MouseArea {
        anchors.fill: parent
        onClicked: checked = !checked
    }
}
