import {
    Card,
    Col,
    Button,
    Modal
} from "react-bootstrap";
import React, { useState, Fragment } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import * as Icon from "@fortawesome/free-solid-svg-icons";
import { v4 as uuidv4 } from 'uuid';
import { CPanelController } from "../../data/panel"
import { PanelController } from "../../data/panel";

export type PanelProps = {
    panelBodyShown?: boolean,
    title: string,
    headerButtons?: React.ReactNode | React.ReactNode[],
    children?: React.ReactNode | React.ReactNode[]
}

export function Panel(props: PanelProps) {
    let { title, headerButtons, panelBodyShown } = props;

    let [panelButtonsId] = useState(() => uuidv4());

    let [shown, updateShown] = useState(true);

    let panelController = new PanelController({
        buttonPortalId: panelButtonsId,
        // upward communication is poor practice, this should be avoided or done another way
        onChangeShown: (shown) => {
            updateShown(shown)
        }
    })

    return (
        <CPanelController.Provider value={panelController}>
            <Card style={{ display: shown ? undefined: 'none' }}>
                <Card.Header className="lead bg-info bg-opacity-25">
                    {title}
                    <div className="float-end">
                        <div id={panelButtonsId} className="d-inline"></div>
                        {headerButtons}
                    </div>
                </Card.Header>
                {(panelBodyShown !== undefined ? panelBodyShown : true) &&
                    <Card.Body>
                        {props.children}
                    </Card.Body>
                }
            </Card>
        </CPanelController.Provider>
    );
}

export type ModalPanelProps = {
    modalChildren?: React.ReactNode | React.ReactNode[],
    modalShown?: boolean,
    onModalShow?: (show: boolean) => void
} & PanelProps

export function ModalPanel(props: ModalPanelProps) {
    let { modalChildren, headerButtons, ...panelProps } = props;

    let hasModal = !!modalChildren;

    if(hasModal) {
        if(!headerButtons) {
            headerButtons = [];
        }
        if(!Array.isArray(headerButtons)) {
            headerButtons = [headerButtons];
        }
        (headerButtons as React.ReactNode[]).push(
            <a className="ms-2" onClick={() => props.onModalShow && props.onModalShow(true)}><FontAwesomeIcon icon={Icon.faPencil} fixedWidth /></a>
        )
    }

    return (
        <Panel {...panelProps} headerButtons={headerButtons}>
            {hasModal && <Modal show={props.modalShown} onHide={() => props.onModalShow && props.onModalShow(false)} size="lg">
                <Modal.Header className="lead bg-info bg-opacity-25">
                    {props.title}
                </Modal.Header>
                <Modal.Body>
                    {modalChildren}
                </Modal.Body>
            </Modal>}
        </Panel>
    )
}

export function ViewPanelActionButtons(props: { onSave: () => void, onCancel: () => void, canSave: boolean }) {
    let { canSave, onSave, onCancel } = props;
    return (
        <Col className="text-center sr-form-action-buttons" sm={12}>
            <Button onClick={onSave} disabled={!canSave} variant="primary">Save Changes</Button>
            <Button onClick={onCancel} variant="light" className="ms-1">Cancel</Button>
        </Col>
    )
}

export type EditorPanelProps = {
    submit: () => void,
    cancel: () => void,
    showButtons: boolean,
    children: React.ReactNode | React.ReactNode[],
    modalChildren: React.ReactNode | React.ReactNode[],
    formValid: boolean,
    title: string,
    id: string
}

// TODO: garsuga, this component should be deleted when no longer needed
export function EditorPanel(props: EditorPanelProps) {
    let {
        submit,
        cancel,
        showButtons,
        children,
        modalChildren,
        formValid,
        title
    } = props;
    let [modalShown, updateModalShown] = useState(false);
    // TODO: garsuga, panel needs to be corrected after it is no longer in a layout
    let [panelBodyShown, updatePanelBodyShown] = useState(true);

    let _cancel = () => {
        updateModalShown(false);
        cancel();
    }

    let _submit = () => {
        updateModalShown(false);
        submit();
    }

    let actionButtons = <ViewPanelActionButtons canSave={formValid} onSave={_submit} onCancel={_cancel}></ViewPanelActionButtons>

    // TODO: should this cancel changes on modal hide??
    return (
        <ModalPanel title={title} panelBodyShown={panelBodyShown} onModalShow={updateModalShown} modalShown={modalShown} modalChildren={(
            <>
                {modalChildren}
                {showButtons &&
                    <Fragment>
                        {actionButtons}
                    </Fragment>
                }
            </>
        )}>
            {children}
            {showButtons && actionButtons}
        </ModalPanel>
    )
}
