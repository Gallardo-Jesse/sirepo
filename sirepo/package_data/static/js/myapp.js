'use strict';

var srlog = SIREPO.srlog;
var srdbg = SIREPO.srdbg;

SIREPO.app.config(() => {
    SIREPO.appReportTypes = `
        <div data-ng-switch-when="buttons" data-buttons-report="" class="sr-plot" data-model-name="{{ modelKey }}" data-report-id="reportId"></div>
        <div data-ng-switch-when="icons" data-icons-report="" class="sr-plot" data-model-name="{{ modelKey }}" data-report-id="reportId"></div>
    `;
});

SIREPO.app.controller('MyAppGuiController', function (appState, panelState, $scope) {
    var self = this;
});


SIREPO.app.controller('MyAppSourceController', function (appState, panelState, $scope) {
    var self = this;

    function handleDogDisposition() {
        panelState.showField('dog', 'favoriteTreat', appState.models.dog.disposition == 'friendly');
    }

    appState.whenModelsLoaded($scope, function() {
        // after the model data is available, hide/show the
        // favoriteTreat field depending on the disposition
        handleDogDisposition();
        appState.watchModelFields($scope, ['dog.disposition'], function() {
            // respond to changes in the disposition field value
            handleDogDisposition();
        });
    });
});

SIREPO.app.directive('appFooter', function() {
    return {
        restrict: 'A',
        scope: {
            nav: '=appFooter',
        },
        template: `
            <div data-common-footer="nav"></div>
        `,
    };
});

SIREPO.app.directive('appHeader', function(appState, panelState) {
    return {
        restrict: 'A',
        scope: {
            nav: '=appHeader',
        },
        template: `
            <div data-app-header-brand="nav"></div>
            <div data-app-header-left="nav"></div>
            <div data-app-header-right="nav">
              <app-header-right-sim-loaded>
                <div data-sim-sections="">
                  <li class="sim-section" data-ng-class="{active: nav.isActive('source')}"><a href data-ng-click="nav.openSection('source')"><span class="glyphicon glyphicon-flash"></span> Source</a></li>
                  <li class="sim-section" data-ng-class="{active: nav.isActive('gui')}"><a href data-ng-click="nav.openSection('gui')"><span class="glyphicon glyphicon-education"></span> GUI Demo</a></li>
                </div>
              </app-header-right-sim-loaded>
              <app-settings>
              </app-settings>
              <app-header-right-sim-list>
              </app-header-right-sim-list>
            </div>
        `,
    };
});

SIREPO.app.directive('buttonsReport', function() {
    return {
        restrict: 'A',
        scope: {
        },
        template: `
            <div class="row">
                <div class="col col-md-6">
                    <div style="padding: 8px 8px;"><label>Action Buttons</label><span data-sr-tooltip="Proposed class change from btn-info to btn-primary"></span></div>
                    <span style="padding: 8px 8px;"><button class="btn btn-primary btn-xs" title="Move up"><span class="glyphicon glyphicon-arrow-up"></span></button></span>
                    <span style="padding: 8px 8px;"><button class="btn btn-primary btn-xs" title="Move down"><span class="glyphicon glyphicon-arrow-down"></span></button></span>
                    <span style="padding: 8px 8px;"><button class="btn btn-primary btn-xs" title="Copy"><span class="glyphicon glyphicon-duplicate"></span></button></span>
                    <span style="padding: 8px 8px;"><button class="btn btn-primary btn-xs" title="Edit"><span class="glyphicon glyphicon-pencil"></span></button></span>
                    <span style="padding: 8px 8px;"><button class="btn btn-danger btn-xs" title="Delete"><span class="glyphicon glyphicon-remove"></span></button></span>
                </div>
                <div class="col col-md-6">
                    <div style="padding: 8px 8px;"><label>Dialog Buttons</label></div>
                    <button class="btn btn-primary"">Save Changes</button>
                    <button class="btn btn-default">Cancel</button>
                </div>
            </div>
        `,
        controller: function($scope) {
        },
    };
});

SIREPO.app.directive('iconsReport', function() {
    return {
        restrict: 'A',
        scope: {
        },
        template: `
            <div class="row">
                <div class="col col-md-12">
                    <div data-ng-repeat="group in iconGroups track by group.name" style="padding: 8px 8px;"><label>{{ group.title }} Icons</label>
                        <table class="table table-striped table-condensed radia-table-dialog">
                            <thead>
                                <th>{{ group.title }}</th>
                                <th>Icon</th>
                                <th>Color</th>
                                <th>Code</th>
                            </thead>
                            <tbody>
                                <tr data-ng-repeat="item in group.icons track by $index">
                                    <td>{{ item.title }}</td>
                                    <td><span class="glyphicon glyphicon-{{ item.glyphicon }} {{ item.classes }}" style="padding: 8px 8px; color:{{ item.color }};" title="{{ item.title }}"></span></td>
                                    <td>{{ item.color || 'Default' }}</td>
                                    <td data-ng-click="copyCode(group, item)" style="cursor:copy;"><code id="{{ codeId(group, item) }}">&lt;span class="glyphicon glyphicon-{{ item.glyphicon }} {{ item.classes }}" title="{{ item.title }}"&gt;&lt;/span&gt;</code></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
            </div>
        `,
        controller: function($scope, $element) {
            $scope.iconGroups = [
                {
                    name: 'status',
                    title: 'Status',
                    icons: [
                        {
                            type: 'canceled',
                            title: 'Canceled',
                            glyphicon: 'ban-circle',
                        },
                        {
                            type: 'completed', 
                            title: 'Completed',
                            glyphicon: 'ok-circle',
                            color: 'green',
                        },
                        {
                            type: 'error',
                            title: 'Error',
                            glyphicon: 'remove',
                            color: 'red',
                        },
                        {
                            type: 'missing',
                            title: 'Missing',
                            glyphicon: 'question-sign',
                        },
                        {
                            type: 'none',
                            title: 'None / Not Started',
                            glyphicon: 'minus',
                        },
                        {
                            type: 'pending',
                            title: 'Pending',
                            glyphicon: 'hourglass',
                        },
                        {
                            type: 'running',
                            title: 'Running',
                            glyphicon: 'refresh',
                            classes: 'running-icon',
                        },
                    ],
                },
            ];

            $scope.codeId = (group, item) => `code-${group.name}-${item.type}`;

            $scope.copyCode = (group, item) => {
                navigator.clipboard.writeText(
                    $($element).find(`code#${$scope.codeId(group, item)}`).text()
                );
            };
        },
    };
});