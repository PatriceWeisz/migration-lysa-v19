#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULES STANDARDS COMPLETS ODOO v16-17-18
==========================================
Configuration de TOUS les modules standard Odoo
Même non installés - Framework UNIVERSEL
"""

def obtenir_modules_comptabilite():
    """Tous les modules comptabilité"""
    return {
        'account.account': {'ordre': 100},
        'account.account.type': {'ordre': 95},
        'account.group': {'ordre': 98},
        'account.tax': {'ordre': 105},
        'account.tax.group': {'ordre': 103},
        'account.tax.repartition.line': {'ordre': 107},
        'account.journal': {'ordre': 110},
        'account.journal.group': {'ordre': 108},
        'account.fiscal.position': {'ordre': 115},
        'account.fiscal.position.account': {'ordre': 117},
        'account.fiscal.position.tax': {'ordre': 118},
        'account.payment.term': {'ordre': 120},
        'account.payment.term.line': {'ordre': 122},
        'account.analytic.plan': {'ordre': 125},
        'account.analytic.account': {'ordre': 130},
        'account.analytic.distribution': {'ordre': 132},
        'account.budget.post': {'ordre': 135},
        'crossovered.budget': {'ordre': 140},
        'crossovered.budget.lines': {'ordre': 142},
        'account.reconcile.model': {'ordre': 145},
        'account.reconcile.model.line': {'ordre': 147},
        'account.cash.rounding': {'ordre': 150},
        'account.incoterms': {'ordre': 152},
        'account.asset': {'ordre': 155},
        'account.asset.category': {'ordre': 153},
    }

def obtenir_modules_ventes():
    """Tous les modules ventes"""
    return {
        'sale.order': {'ordre': 2000},
        'sale.order.line': {'ordre': 2005},
        'sale.order.option': {'ordre': 2007},
        'sale.quote.template': {'ordre': 1300},
        'sale.quote.line': {'ordre': 1305},
        'sale.subscription': {'ordre': 2010},
        'sale.subscription.template': {'ordre': 1310},
        'crm.team': {'ordre': 1200},
        'crm.stage': {'ordre': 1205},
        'crm.lead': {'ordre': 2015},
        'crm.lead.tag': {'ordre': 1210},
        'crm.lost.reason': {'ordre': 1212},
        'utm.campaign': {'ordre': 1215},
        'utm.medium': {'ordre': 1217},
        'utm.source': {'ordre': 1219},
    }

def obtenir_modules_achats():
    """Tous les modules achats"""
    return {
        'purchase.order': {'ordre': 2020},
        'purchase.order.line': {'ordre': 2025},
        'purchase.requisition': {'ordre': 2027},
        'purchase.requisition.line': {'ordre': 2029},
        'product.supplierinfo': {'ordre': 1320},
    }

def obtenir_modules_stock():
    """Tous les modules stock/inventaire"""
    return {
        'stock.warehouse': {'ordre': 600},
        'stock.location': {'ordre': 605},
        'stock.location.route': {'ordre': 607},
        'stock.route': {'ordre': 606},
        'stock.rule': {'ordre': 608},
        'stock.picking.type': {'ordre': 610},
        'stock.picking': {'ordre': 2030},
        'stock.move': {'ordre': 2035},
        'stock.move.line': {'ordre': 2040},
        'stock.quant': {'ordre': 2045},
        'stock.quant.package': {'ordre': 2047},
        'stock.production.lot': {'ordre': 615},
        'stock.lot.serial': {'ordre': 617},
        'stock.inventory': {'ordre': 2050},
        'stock.scrap': {'ordre': 2052},
        'stock.warehouse.orderpoint': {'ordre': 620},
        'stock.putaway.rule': {'ordre': 622},
    }

def obtenir_modules_fabrication():
    """Tous les modules manufacturing"""
    return {
        'mrp.bom': {'ordre': 1400},
        'mrp.bom.line': {'ordre': 1405},
        'mrp.bom.byproduct': {'ordre': 1407},
        'mrp.production': {'ordre': 2055},
        'mrp.workorder': {'ordre': 2060},
        'mrp.workcenter': {'ordre': 625},
        'mrp.workcenter.productivity': {'ordre': 2062},
        'mrp.routing': {'ordre': 1410},
        'mrp.routing.workcenter': {'ordre': 1412},
        'quality.point': {'ordre': 630},
        'quality.check': {'ordre': 2065},
        'quality.alert': {'ordre': 2067},
    }

def obtenir_modules_point_vente():
    """Tous les modules Point de Vente"""
    return {
        'pos.config': {'ordre': 1500},
        'pos.session': {'ordre': 2070},
        'pos.order': {'ordre': 2075},
        'pos.order.line': {'ordre': 2080},
        'pos.payment': {'ordre': 2082},
        'pos.payment.method': {'ordre': 1505},
        'pos.category': {'ordre': 1507},
    }

def obtenir_modules_marketing():
    """Tous les modules marketing"""
    return {
        'marketing.campaign': {'ordre': 1600},
        'marketing.activity': {'ordre': 1605},
        'marketing.participant': {'ordre': 2085},
        'mailing.mailing': {'ordre': 1610},
        'mailing.list': {'ordre': 1612},
        'mailing.contact': {'ordre': 1615},
        'mailing.trace': {'ordre': 2090},
        'link.tracker': {'ordre': 1620},
        'link.tracker.click': {'ordre': 2095},
        'social.media': {'ordre': 1625},
        'social.post': {'ordre': 1630},
    }

def obtenir_modules_helpdesk():
    """Tous les modules helpdesk/support"""
    return {
        'helpdesk.team': {'ordre': 1700},
        'helpdesk.stage': {'ordre': 1705},
        'helpdesk.ticket': {'ordre': 2100},
        'helpdesk.ticket.type': {'ordre': 1707},
        'helpdesk.sla': {'ordre': 1710},
    }

def obtenir_modules_planning():
    """Tous les modules planning/ressources"""
    return {
        'planning.slot': {'ordre': 2105},
        'planning.role': {'ordre': 1800},
        'planning.template': {'ordre': 1805},
        'resource.calendar': {'ordre': 650},
        'resource.calendar.attendance': {'ordre': 652},
        'resource.calendar.leaves': {'ordre': 654},
        'calendar.event': {'ordre': 2110},
        'calendar.event.type': {'ordre': 1810},
    }

def obtenir_modules_maintenance():
    """Tous les modules maintenance"""
    return {
        'maintenance.equipment': {'ordre': 1900},
        'maintenance.equipment.category': {'ordre': 1895},
        'maintenance.request': {'ordre': 2115},
        'maintenance.stage': {'ordre': 1905},
        'maintenance.team': {'ordre': 1907},
    }

def obtenir_modules_signature():
    """Tous les modules signature électronique"""
    return {
        'sign.template': {'ordre': 1950},
        'sign.item': {'ordre': 1955},
        'sign.request': {'ordre': 2120},
        'sign.request.item': {'ordre': 2125},
    }

def obtenir_modules_appointment():
    """Tous les modules rendez-vous"""
    return {
        'appointment.type': {'ordre': 2000},
        'appointment.invite': {'ordre': 2005},
        'calendar.appointment.type': {'ordre': 2003},
    }

def obtenir_modules_fleet():
    """Tous les modules parc automobile"""
    return {
        'fleet.vehicle': {'ordre': 2200},
        'fleet.vehicle.model': {'ordre': 2195},
        'fleet.vehicle.model.brand': {'ordre': 2190},
        'fleet.vehicle.log.contract': {'ordre': 2205},
        'fleet.vehicle.log.services': {'ordre': 2210},
    }

def obtenir_modules_survey():
    """Tous les modules sondages/questionnaires"""
    return {
        'survey.survey': {'ordre': 2300},
        'survey.question': {'ordre': 2305},
        'survey.question.answer': {'ordre': 2307},
        'survey.user_input': {'ordre': 2310},
        'survey.user_input.line': {'ordre': 2315},
    }

def obtenir_modules_iot():
    """Tous les modules IoT"""
    return {
        'iot.box': {'ordre': 2400},
        'iot.device': {'ordre': 2405},
    }

def obtenir_modules_knowledge():
    """Tous les modules knowledge/wiki"""
    return {
        'knowledge.article': {'ordre': 2500},
        'knowledge.article.favorite': {'ordre': 2505},
    }

def obtenir_modules_livraison():
    """Tous les modules livraison/expédition"""
    return {
        'delivery.carrier': {'ordre': 1850},
        'delivery.price.rule': {'ordre': 1852},
        'stock.package.type': {'ordre': 635},
    }

def obtenir_tous_modules_standards():
    """
    Retourne TOUS les modules standards Odoo v16-17-18
    
    Returns:
        dict {module: config}
    """
    tous_modules = {}
    
    tous_modules.update(obtenir_modules_comptabilite())
    tous_modules.update(obtenir_modules_ventes())
    tous_modules.update(obtenir_modules_achats())
    tous_modules.update(obtenir_modules_stock())
    tous_modules.update(obtenir_modules_fabrication())
    tous_modules.update(obtenir_modules_point_vente())
    tous_modules.update(obtenir_modules_marketing())
    tous_modules.update(obtenir_modules_helpdesk())
    tous_modules.update(obtenir_modules_planning())
    tous_modules.update(obtenir_modules_maintenance())
    tous_modules.update(obtenir_modules_signature())
    tous_modules.update(obtenir_modules_appointment())
    tous_modules.update(obtenir_modules_fleet())
    tous_modules.update(obtenir_modules_survey())
    tous_modules.update(obtenir_modules_iot())
    tous_modules.update(obtenir_modules_knowledge())
    tous_modules.update(obtenir_modules_livraison())
    
    return tous_modules

# =============================================================================
# STATISTIQUES
# =============================================================================

if __name__ == '__main__':
    modules = obtenir_tous_modules_standards()
    
    print("="*70)
    print("MODULES STANDARDS ODOO v16-17-18")
    print("="*70)
    print(f"Total modules configurés: {len(modules)}")
    print("")
    
    categories = {
        'Comptabilité': obtenir_modules_comptabilite(),
        'Ventes': obtenir_modules_ventes(),
        'Achats': obtenir_modules_achats(),
        'Stock': obtenir_modules_stock(),
        'Fabrication': obtenir_modules_fabrication(),
        'Point de Vente': obtenir_modules_point_vente(),
        'Marketing': obtenir_modules_marketing(),
        'Helpdesk': obtenir_modules_helpdesk(),
        'Planning': obtenir_modules_planning(),
        'Maintenance': obtenir_modules_maintenance(),
        'Signature': obtenir_modules_signature(),
        'Rendez-vous': obtenir_modules_appointment(),
        'Parc Auto': obtenir_modules_fleet(),
        'Sondages': obtenir_modules_survey(),
        'IoT': obtenir_modules_iot(),
        'Knowledge': obtenir_modules_knowledge(),
        'Livraison': obtenir_modules_livraison(),
    }
    
    for cat, mods in categories.items():
        print(f"{cat:25s}: {len(mods):>3} modules")
    
    print("="*70)
    print(f"TOTAL: {len(modules)} modules")
    print("="*70)
    print("\nFramework UNIVERSEL - Compatible avec TOUTE base Odoo!")

