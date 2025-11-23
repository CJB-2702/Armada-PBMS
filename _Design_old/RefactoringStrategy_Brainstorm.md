# Refactoring Strategy: Moving Business Logic from Data Layer to Business Layer

## Current State Analysis

### Business Logic Currently in Data Layer

1. **Asset Model** (`app/data/core/asset_info/asset.py`):
   - `_automatic_detail_insertion_enabled` (class-level flag)
   - `_after_insert` event listener (creates events + triggers detail creation)
   - `create_detail_table_rows()` method (delegates to AssetDetailFactory)
   - `enable_automatic_detail_insertion()` / `disable_automatic_detail_insertion()` class methods
   - Event listener registration at module load time

2. **MakeModel Model** (`app/data/core/asset_info/make_model.py`):
   - `_automatic_detail_insertion_enabled` (class-level flag)
   - `_after_insert` event listener (creates events + triggers detail creation)
   - `create_detail_table_rows()` method (delegates to ModelDetailFactory)
   - `enable_automatic_detail_insertion()` / `disable_automatic_detail_insertion()` class methods
   - Event listener registration at module load time

### Current Architecture Flow

```
AssetFactory.create_asset()
  → db.session.add(asset)
  → db.session.commit()
    → SQLAlchemy after_insert event fires
      → Asset._after_insert()
        → Creates Event
        → Calls asset.create_detail_table_rows()
          → AssetDetailFactory.create_detail_table_rows(asset)
```

## Design Principles to Apply

### 1. **Separation of Concerns (SoC)**
- Data models should only contain data structure and basic validation
- Business logic belongs in the business layer
- Event creation and detail insertion are business concerns, not data concerns

### 2. **Single Responsibility Principle (SRP)**
- Asset model should only be responsible for representing asset data
- Context classes should handle business operations
- Factories should handle object creation with business rules

### 3. **Dependency Inversion Principle (DIP)**
- High-level modules (business) should not depend on low-level modules (data)
- Both should depend on abstractions
- Core modules should not depend on feature modules (assets)

### 4. **Open/Closed Principle (OCP)**
- AssetContext should be open for extension (AssetDetailsContext)
- Should be closed for modification
- Need a way to extend behavior without modifying core

### 5. **Strategy Pattern**
- Different strategies for asset creation (with/without detail insertion)
- Context can choose strategy based on configuration

### 6. **Factory Pattern** (Already in use)
- AssetFactory handles asset creation
- Should also handle post-creation operations (events, details)

### 7. **Decorator Pattern / Wrapper Pattern**
- AssetDetailsContext wraps AssetContext
- Could use composition or inheritance

### 8. **Observer Pattern** (Currently misused)
- SQLAlchemy events are observers, but they're in the wrong layer
- Should move observation to business layer

### 9. **Dependency Injection**
- Context classes could accept strategies/factories as dependencies
- Allows for different behaviors without hardcoding

### 10. **Module Independence**
- Core modules must not depend on feature modules
- Feature modules can depend on core
- Exception: inventory depends on maintenance (explicitly allowed)

## Strategy Options

### Strategy 1: Factory-Based Creation with Post-Creation Hooks

**Concept**: Move all business logic to factories. Factories handle creation, event creation, and detail insertion.

**Approach**:
- Remove all event listeners from data models
- Remove `create_detail_table_rows()` from Asset/MakeModel
- Remove `_automatic_detail_insertion_enabled` flags
- AssetFactory becomes responsible for:
  - Creating asset
  - Creating creation event
  - Conditionally creating detail rows (if enabled)
- MakeModelFactory becomes responsible for same for models

**Pros**:
- Clean separation: data layer is pure data
- Explicit control flow (no hidden event listeners)
- Easy to test (no SQLAlchemy event mocking needed)
- Factory can accept configuration (enable_detail_insertion parameter)

**Cons**:
- Requires all asset creation to go through factory (enforcement needed)
- Direct ORM usage bypasses factory (but this might be acceptable for simple cases)

**Module Independence**:
- ✅ Core factories (if any) stay in core
- ✅ AssetDetailFactory stays in assets module
- ✅ Core AssetFactory doesn't depend on assets module

**Implementation Pattern**:
```python
# app/buisness/core/asset_factory.py (or keep in assets?)
class AssetFactory:
    @classmethod
    def create_asset(cls, created_by_id=None, enable_detail_insertion=True, **kwargs):
        asset = Asset(**kwargs)
        db.session.add(asset)
        db.session.flush()  # Get ID
        
        # Create event (business logic)
        EventFactory.create_asset_creation_event(asset, created_by_id)
        
        # Conditionally create details (if enabled and factory available)
        if enable_detail_insertion:
            cls._create_detail_rows(asset)
        
        if commit:
            db.session.commit()
        return asset
    
    @classmethod
    def _create_detail_rows(cls, asset):
        # Lazy import to avoid circular dependency
        try:
            from app.buisness.assets.factories.asset_detail_factory import AssetDetailFactory
            AssetDetailFactory.create_detail_table_rows(asset)
        except ImportError:
            # Assets module not available - skip detail creation
            pass
```

### Strategy 2: Context-Based Creation with Strategy Pattern

**Concept**: AssetContext becomes the primary interface for asset operations, including creation. Context can be configured with strategies.

**Approach**:
- AssetContext has a `create()` class method or factory method
- Context accepts a "creation strategy" that defines post-creation behavior
- Default strategy: create asset + event
- Extended strategy (when assets module available): create asset + event + details

**Pros**:
- Consistent interface (all operations through context)
- Strategy pattern allows different behaviors
- Context can be "upgraded" to AssetDetailsContext when needed

**Cons**:
- Context classes become more complex
- Mixing creation and management concerns
- May violate SRP (context manages AND creates)

**Module Independence**:
- ✅ Core AssetContext doesn't depend on assets module
- ✅ AssetDetailsContext extends AssetContext
- ⚠️ Need careful design to avoid circular dependencies

**Implementation Pattern**:
```python
# app/buisness/core/asset_context.py
class AssetContext:
    @classmethod
    def create(cls, created_by_id=None, **kwargs):
        """Create asset with basic operations"""
        asset = Asset(**kwargs)
        db.session.add(asset)
        db.session.flush()
        
        # Create event
        EventFactory.create_asset_creation_event(asset, created_by_id)
        
        # Return context for the new asset
        return cls(asset)
    
    @classmethod
    def create_with_details(cls, created_by_id=None, **kwargs):
        """Create asset with detail insertion - returns AssetDetailsContext"""
        # Create basic asset
        context = cls.create(created_by_id, **kwargs)
        
        # Upgrade to AssetDetailsContext and create details
        from app.buisness.assets.asset_details_context import AssetDetailsContext
        details_context = AssetDetailsContext(context.asset)
        details_context.create_detail_rows()
        
        return details_context
```

### Strategy 3: Composition with Creation Managers

**Concept**: Separate creation logic into dedicated "CreationManager" classes. Contexts use managers for creation.

**Approach**:
- Create `AssetCreationManager` in business layer
- Manager handles: creation, events, detail insertion
- Context classes use managers for creation operations
- Managers can be swapped/injected

**Pros**:
- Clear separation: managers create, contexts manage
- Easy to test managers independently
- Can have different managers for different scenarios
- Follows SRP

**Cons**:
- Additional abstraction layer
- More classes to maintain
- Need to decide where managers live (core vs assets module)

**Module Independence**:
- ✅ Core AssetCreationManager in core (basic creation + events)
- ✅ AssetDetailCreationManager in assets module (extends or composes with core)
- ✅ Core doesn't depend on assets module

**Implementation Pattern**:
```python
# app/buisness/core/asset_creation_manager.py
class AssetCreationManager:
    def create_asset(self, created_by_id=None, **kwargs):
        asset = Asset(**kwargs)
        db.session.add(asset)
        db.session.flush()
        self._create_creation_event(asset, created_by_id)
        return asset

# app/buisness/assets/asset_detail_creation_manager.py
class AssetDetailCreationManager(AssetCreationManager):
    def create_asset(self, created_by_id=None, enable_details=True, **kwargs):
        asset = super().create_asset(created_by_id, **kwargs)
        if enable_details:
            AssetDetailFactory.create_detail_table_rows(asset)
        return asset
```

### Strategy 4: Plugin/Extension System

**Concept**: Core provides hooks/extension points. Feature modules register extensions.

**Approach**:
- AssetContext has extension points (post_creation_hooks)
- Assets module registers detail insertion hook
- When AssetContext creates asset, it calls registered hooks
- AssetDetailsContext registers the hook automatically

**Pros**:
- Very flexible and extensible
- Core remains independent
- Feature modules extend core without modifying it
- Follows Open/Closed Principle

**Cons**:
- More complex architecture
- Hook registration mechanism needed
- Potential for hook ordering issues
- May be over-engineered for current needs

**Module Independence**:
- ✅ Core defines extension points
- ✅ Assets module registers extensions
- ✅ No circular dependencies

**Implementation Pattern**:
```python
# app/buisness/core/asset_context.py
class AssetContext:
    _post_creation_hooks = []
    
    @classmethod
    def register_post_creation_hook(cls, hook):
        cls._post_creation_hooks.append(hook)
    
    @classmethod
    def create(cls, created_by_id=None, **kwargs):
        asset = Asset(**kwargs)
        db.session.add(asset)
        db.session.flush()
        
        # Create event
        EventFactory.create_asset_creation_event(asset, created_by_id)
        
        # Call registered hooks
        for hook in cls._post_creation_hooks:
            hook(asset)
        
        return cls(asset)

# app/buisness/assets/asset_details_context.py (on module import)
def _detail_creation_hook(asset):
    AssetDetailFactory.create_detail_table_rows(asset)

AssetContext.register_post_creation_hook(_detail_creation_hook)
```

### Strategy 5: Conditional Context Class Selection

**Concept**: Factory/Manager returns appropriate context class based on configuration. AssetContext vs AssetDetailsContext.

**Approach**:
- Factory method that returns AssetContext or AssetDetailsContext
- Configuration determines which context to use
- AssetDetailsContext extends AssetContext, so it's always compatible
- When details enabled, return AssetDetailsContext; otherwise AssetContext

**Pros**:
- Simple and straightforward
- Type system helps (AssetDetailsContext IS-A AssetContext)
- Easy to understand
- No complex patterns needed

**Cons**:
- Need to decide where factory lives
- May need to check if assets module is available
- Import-time decisions vs runtime decisions

**Module Independence**:
- ✅ Core factory returns AssetContext
- ✅ Assets module provides factory that returns AssetDetailsContext
- ✅ Or: core factory checks for assets module availability

**Implementation Pattern**:
```python
# app/buisness/core/asset_factory.py
class AssetFactory:
    @classmethod
    def create_asset_context(cls, asset_id_or_instance, enable_details=False):
        """Create appropriate context based on configuration"""
        if enable_details:
            # Try to use AssetDetailsContext if available
            try:
                from app.buisness.assets.asset_details_context import AssetDetailsContext
                return AssetDetailsContext(asset_id_or_instance)
            except ImportError:
                # Assets module not available, fall back to basic context
                return AssetContext(asset_id_or_instance)
        return AssetContext(asset_id_or_instance)
    
    @classmethod
    def create(cls, created_by_id=None, enable_details=True, **kwargs):
        asset = Asset(**kwargs)
        db.session.add(asset)
        db.session.flush()
        
        # Create event
        EventFactory.create_asset_creation_event(asset, created_by_id)
        
        # Create details if enabled
        if enable_details:
            try:
                from app.buisness.assets.factories.asset_detail_factory import AssetDetailFactory
                AssetDetailFactory.create_detail_table_rows(asset)
            except ImportError:
                pass
        
        # Return appropriate context
        return cls.create_asset_context(asset, enable_details)
```

## Recommended Hybrid Approach

### Primary Strategy: Factory-Based with Conditional Context Return (Strategy 1 + Strategy 5)

**Rationale**:
- Clean separation: factories handle creation logic
- Data models remain pure (no business logic)
- Context selection based on needs
- Maintains module independence
- Simple to understand and maintain

**Implementation Plan**:

1. **Remove from Data Layer**:
   - Remove `_automatic_detail_insertion_enabled` from Asset and MakeModel
   - Remove `_after_insert` event listeners
   - Remove `create_detail_table_rows()` methods
   - Remove `enable_automatic_detail_insertion()` / `disable_automatic_detail_insertion()` methods
   - Remove event listener registrations

2. **Enhance Factories**:
   - Move event creation to factories (or EventFactory)
   - Move detail creation logic to factories
   - Factories accept `enable_detail_insertion` parameter
   - Factories use lazy imports to avoid circular dependencies

3. **Context Enhancement**:
   - AssetContext remains in core (basic operations)
   - AssetDetailsContext extends AssetContext (detail operations)
   - Factory can return either context type based on configuration
   - Context classes can have `create()` methods that delegate to factories

4. **Module Independence**:
   - Core factories don't import from assets module
   - Use try/except ImportError for optional features
   - Assets module factories extend or compose with core factories

### Alternative: Strategy 2 (Context-Based) if Context is Primary Interface

If AssetContext is meant to be the primary interface for all asset operations (not just management), then Strategy 2 makes more sense:

- All creation goes through context
- Context can be "upgraded" to AssetDetailsContext
- Consistent API: `AssetContext.create()` vs `AssetContext(asset_id)`

## Key Design Decisions Needed

### Decision 1: Where Should Creation Logic Live?
- **Option A**: Factories (current approach, recommended)
- **Option B**: Context classes (if context is primary interface)
- **Option C**: Separate CreationManager classes

### Decision 2: How to Handle Optional Features?
- **Option A**: Lazy imports with try/except (simple, recommended)
- **Option B**: Plugin/hook system (more flexible, more complex)
- **Option C**: Dependency injection (most flexible, most complex)

### Decision 3: Event Creation Location?
- **Option A**: Factories (recommended - creation is business logic)
- **Option B**: EventFactory (dedicated factory for events)
- **Option C**: Context classes (if context handles all operations)

### Decision 4: Configuration Management?
- **Option A**: Parameter-based (enable_detail_insertion=True/False)
- **Option B**: Global configuration/settings
- **Option C**: Context-level configuration

### Decision 5: Backward Compatibility?
- How to handle existing code that uses `Asset.enable_automatic_detail_insertion()`?
- Migration path for existing event listeners?
- Should factories be drop-in replacements?

## Module Independence Considerations

### Core Module Dependencies
- ✅ Core should NOT import from assets module
- ✅ Core should NOT import from maintenance module
- ✅ Core should NOT import from inventory module
- ✅ Core should NOT import from dispatching module

### Assets Module Dependencies
- ✅ Assets can import from core
- ❌ Assets should NOT import from maintenance (unless needed)
- ❌ Assets should NOT import from inventory
- ❌ Assets should NOT import from dispatching

### Lazy Import Pattern
```python
# In core factory
def _create_details_if_enabled(asset):
    try:
        from app.buisness.assets.factories.asset_detail_factory import AssetDetailFactory
        AssetDetailFactory.create_detail_table_rows(asset)
    except ImportError:
        # Assets module not available - skip
        pass
```

## Testing Considerations

### Benefits of Removing Event Listeners
- ✅ No need to mock SQLAlchemy events
- ✅ Explicit control flow (easier to test)
- ✅ Can test factories independently
- ✅ Can test with/without detail insertion easily

### Test Scenarios
1. Asset creation without detail insertion
2. Asset creation with detail insertion (when assets module available)
3. Asset creation with detail insertion (when assets module NOT available)
4. MakeModel creation scenarios (same as above)
5. Event creation verification
6. Module independence verification

## Migration Strategy

### Phase 1: Preparation
1. Ensure all asset creation goes through AssetFactory
2. Document current event listener behavior
3. Create tests for current behavior

### Phase 2: Implementation
1. Add new factory methods with detail insertion parameter
2. Update factories to handle events and details
3. Keep old methods temporarily (deprecated)

### Phase 3: Migration
1. Update all code to use new factory methods
2. Remove event listeners from data models
3. Remove deprecated methods

### Phase 4: Cleanup
1. Remove unused code
2. Update documentation
3. Verify module independence

## Questions to Resolve

1. **Should AssetContext have a `create()` method, or should creation always go through factories?**
   - If context is primary interface: yes
   - If factory is primary interface: no

2. **How to handle the case where assets module is not available?**
   - Graceful degradation (skip detail creation)
   - Error/warning?
   - Configuration flag?

3. **Should there be a global setting for automatic detail insertion, or always explicit?**
   - Explicit parameter (more control, recommended)
   - Global setting (easier, but less flexible)

4. **What about MakeModel creation?**
   - Same pattern as Asset?
   - Separate factory?
   - Same factory with different methods?

5. **Event creation: separate EventFactory or part of AssetFactory?**
   - Separate (better SRP, recommended)
   - Part of AssetFactory (simpler, but mixes concerns)

